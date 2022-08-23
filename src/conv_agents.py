import abc
import os
import time

import requests
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    BlenderbotForConditionalGeneration,
    BlenderbotTokenizer,
)
from src.conversation import Message
import subprocess
import warnings


class AbstractAgent(abc.ABC):
    """Abstract base class that defines the interface for a conversational agent."""

    def __init__(self, agent_id, role="Other agent"):
        """Make sure to start the server on which you run your GDM, should you have any."""
        self.agent_id = agent_id
        self.role = role

    def act(self, messages) -> Message:
        """Define how to get a reply from the agent."""
        pass

    def get_id(self):
        """Returns the ID of self."""
        return self.agent_id

    def get_role(self):
        """Returns the role of self, as to find out if the message should be tested or not."""
        return self.role

    def setup(self):
        """Method used for setting up the GDM, which may differ from GDM to GDM, if necessary at all."""
        pass

    def shutdown(self):
        """Method used for shutting down the GDM, which may differ from GDM to GDM, if necessary at all."""
        pass


# ------- Different conversational agents implemented


class Human(AbstractAgent):
    """Conversational agent where a human is involved. You need to be present at the keyboard for this to work, as it
    is you who talk with the other agent."""

    def __init__(self, agent_id):
        AbstractAgent.__init__(self, agent_id=agent_id)

    def act(self, conversation):
        response = input("You: ")
        return response


class BlenderBot400M(AbstractAgent):
    """BlenderBot's 400M model as a conversational agent."""

    def __init__(self, agent_id, role="Other agent"):
        AbstractAgent.__init__(self, agent_id=agent_id, role=role)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.name = "facebook/blenderbot-400M-distill"
        self.model = BlenderbotForConditionalGeneration.from_pretrained(self.name).to(
            self.device
        )
        self.tokenizer = BlenderbotTokenizer.from_pretrained(self.name)

        """ self.chat_memory regulates how many previous lines of the conversation that Blenderbot takes in. """
        self.chat_memory = 3  # 1 if role == "Other agent" else 3
        self.do_sample = True if role == "Other agent" else False

    def act(self, messages):
        """Method for producing a response from the Blenderbot400M-model."""
        conv_string = self.__array2blenderstring(messages[-self.chat_memory :])
        if len(conv_string) > 128:
            conv_string = conv_string[-128:]
        inputs = self.tokenizer([conv_string], return_tensors="pt").to(self.device)
        reply_ids = self.model.generate(
            **inputs,
            num_beams=10,
            no_repeat_ngram_size=3,
            do_sample=self.do_sample,
            top_p=0.9,
            top_k=0,
        )
        response = self.tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
        return response

    def __array2blenderstring(self, conversation):
        """Method for inserting the response-separator, as to assist Blenderbot400m in distinguishing what message
        belongs to what GDM."""
        conv_string = " ".join([str(elem) + "</s> <s>" for elem in conversation])
        conv_string = conv_string[: len(conv_string) - 8]
        return conv_string


class BlenderBot90M(AbstractAgent):
    """Blenderbot's 90M model as a conversational agent."""

    def __init__(self, agent_id, role="Other agent"):
        AbstractAgent.__init__(self, agent_id=agent_id, role=role)
        self.device = "cpu"  # "cuda" if torch.cuda.is_available() else "cpu"
        self.name = "facebook/blenderbot_small-90M"
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.name).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.name)

        """ self.chat_memory regulates how many previous lines of the conversation that Blenderbot takes in. """
        self.chat_memory = 1 if role == "Other agent" else 3
        self.do_sample = True if role == "Other agent" else False

    def act(self, messages):
        """Method for producing responses from Blenderbot's 90M-model."""
        conv_string = "\n".join(elem for elem in messages[-self.chat_memory :])
        inputs = self.tokenizer([conv_string], return_tensors="pt").to(self.device)
        reply_ids = self.model.generate(
            **inputs,
            num_beams=10,
            no_repeat_ngram_size=3,
            do_sample=self.do_sample,
            top_p=0.9,
            top_k=0,
        )
        response = self.tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
        return response


class Emely(AbstractAgent):
    def __init__(self, agent_id, role="Other agent"):
        AbstractAgent.__init__(self, agent_id=agent_id, role=role)
        self.URL = "http://localhost:8080/inference"
        self.chat_memory = 6

    def act(self, messages):
        # Inputs the conversation array and outputs a response from Emely
        conv_string = "\n".join([str(elem) for elem in messages[-self.chat_memory :]])
        json_obj = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "text": conv_string,
        }
        r = requests.post(self.URL, json=json_obj)
        response = r.json()["text"]
        return response

    def setup(self):
        success = os.system("docker container restart {}".format(self.agent_id))
        if success != 0:
            os.system(
                "docker run --name {} -d -p 8080:8080 {}".format(
                    self.agent_id, self.agent_id
                )
            )

        """ Delay added as to make sure the docker is ready to receive requests and produce responses. """
        time.sleep(8)

    def shutdown(self):
        os.system("docker container kill {}".format(self.agent_id))
        time.sleep(5)

    def exists(self):
        "Tries to start a container with name agent_id to determine if agent_id was valid"
        exists = True
        if subprocess.run(["docker", "restart", self.agent_id]).returncode:
            if subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    self.agent_id,
                    "-p",
                    "8080:8080",
                    self.agent_id,
                ]
            ).returncode:
                exists = False

        if exists:
            subprocess.run(["docker", "kill", self.agent_id])
        return exists


""" The conversational agents that are currently implemented. This dict is used for interpreting CLI arguments and from
that instantiate conversational agents. """
available_agents = {
    "human": Human,
    "blenderbot90m": BlenderBot90M,
    "blenderbot400m": BlenderBot400M,
    "emely02": Emely,
    "emely03": Emely,
    "emely04": Emely,
    "emely05": Emely,
    "emely06": Emely,
    "luis_han": Emely,
    "jani_peralez": Emely,
    "jeremy_hench": Emely,
}


def load_conv_agent(agents, role="Other agent"):
    """Method used for interpreting the CLI argument string and return instantiated conv_agents."""
    agents = agents.lower()
    agents = agents.split(",")
    list_conv_agents = []
    for agent in agents:
        if agent in available_agents.keys():
            agent_object = available_agents[agent](agent_id=agent, role=role)
        elif "emely" in agent.lower():
            agent_object = Emely(agent_id=agent, role=role)
            if not agent_object.exists():
                warnings.warn(f"Did not find {agent} in supported agents!")
                continue
        else:
            warnings.warn(f"Did not find {agent} in supported agents!")
        list_conv_agents.append(agent_object)
    return list_conv_agents, agents
