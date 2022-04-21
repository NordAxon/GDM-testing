import abc
import os
from datetime import time
import time

import requests
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, BlenderbotForConditionalGeneration, BlenderbotTokenizer
from conversation import Message, Conversation


class AbstractAgent(abc.ABC):
    """ Abstract base class that defines the interface for a conversational agent. """

    @abc.abstractmethod
    def __init__(self, agent_id, role='Other agent'):
        """ Make sure to start the server on which you run your GDM, should you have any. """
        self.agent_id = agent_id
        self.role = role

    @abc.abstractmethod
    def act(self, messages) -> Message:
        """ Define how to get a reply from the agent. """
        pass

    def get_id(self):
        """ Returns the ID of self. """
        return self.agent_id

    def get_role(self):
        """ Returns the role of self, as to find out if the message should be tested or not. """
        return self.role


# ------- Different conversational agents implemented


class Human(AbstractAgent):
    """ Conversational agent where a human is involved. You need to be present at the keyboard for this to work, as it
     is you who talk with the other agent. """

    def __init__(self, agent_id):
        AbstractAgent.__init__(agent_id=agent_id)

    def act(self, conversation):
        response = input("You: ")
        return response


class BlenderBot400M(AbstractAgent):
    """ BlenderBot's 400M model as a conversational agent. """

    def __init__(self, agent_id, role='Other agent'):
        AbstractAgent.__init__(self, agent_id=agent_id, role=role)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.name = 'facebook/blenderbot-400M-distill'
        self.model = BlenderbotForConditionalGeneration.from_pretrained(self.name).to(self.device)
        self.tokenizer = BlenderbotTokenizer.from_pretrained(self.name)

        """ self.chat_memory regulates how many previous lines of the conversation that Blenderbot takes in. """
        self.chat_memory = 3

    def act(self, messages):
        """ Method for producing a response from the Blenderbot400M-model. """
        conv_string = self.__array2blenderstring(messages[-self.chat_memory:])
        if len(conv_string) > 128:
            conv_string = conv_string[-128:]
        inputs = self.tokenizer([conv_string], return_tensors='pt').to(self.device)
        reply_ids = self.model.generate(**inputs, num_beams=10, no_repeat_ngram_size=3)
        response = self.tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
        return response

    def __array2blenderstring(self, conversation):
        """ Method for inserting the response-separator, as to assist Blenderbot400m in distinguishing what message
        belongs to what GDM. """
        conv_string = ' '.join([str(elem) + '</s> <s>' for elem in conversation])
        conv_string = conv_string[:len(conv_string) - 8]
        return conv_string


class BlenderBot90M(AbstractAgent):
    """ Blenderbot's 90M model as a conversational agent. """

    def __init__(self, agent_id, role='Other agent'):
        AbstractAgent.__init__(self, agent_id=agent_id, role=role)
        self.device = "cpu" #"cuda" if torch.cuda.is_available() else "cpu"
        self.name = 'facebook/blenderbot_small-90M'
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.name).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.name)

        """ self.chat_memory regulates how many previous lines of the conversation that Blenderbot takes in. """
        self.chat_memory = 6
        self.do_sample = True if role == "Other agent" else False

    def act(self, messages):
        """ Method for producing responses from Blenderbot's 90M-model."""
        conv_string = '\n'.join(elem for elem in messages[-self.chat_memory:])
        inputs = self.tokenizer([conv_string], return_tensors='pt').to(self.device)
        reply_ids = self.model.generate(**inputs, num_beams=15, no_repeat_ngram_size=3, do_sample=self.do_sample,
                                        top_p=0.8, top_k=0)
        response = self.tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
        return response


class Emely02(AbstractAgent):
    def __init__(self, agent_id, role='Other agent'):
        AbstractAgent.__init__(self, agent_id=agent_id, role=role)
        self.URL = "http://localhost:8080/inference"
        self.chat_memory = 6
        self.emely_id = "emely02"

    def setup(self):
        success = os.system("docker container restart {}".format(self.emely_id, self.emely_id))
        if success != 0:
            os.system("docker run --name {} -d -p 8080:8080 {}".format(self.emely_id, self.emely_id))
        time.sleep(5)

    def act(self, messages):
        # Inputs the conversation array and outputs a response from Emely
        conv_string = '\n'.join([str(elem) for elem in messages[-self.chat_memory:]])
        json_obj = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "text": conv_string
        }
        r = requests.post(self.URL, json=json_obj)
        response = r.json()['text']
        if len(response) > 128:
            response = response[0:128]
        return response

    def shutdown(self):
        os.system("docker container kill {}".format(self.emely_id))
        time.sleep(5)


class Emely03(AbstractAgent):
    def __init__(self, agent_id, role='Other agent'):
        AbstractAgent.__init__(self, agent_id=agent_id, role=role)
        self.URL = "http://localhost:8080/inference"
        self.chat_memory = 6
        self.emely_id = "emely03"

    def setup(self):
        success = os.system("docker container restart {}".format(self.emely_id, self.emely_id))
        if success != 0:
            os.system("docker run --name {} -d -p 8080:8080 {}".format(self.emely_id, self.emely_id))
        time.sleep(5)

    def act(self, messages):
        # Inputs the conversation array and outputs a response from Emely
        conv_string = '\n'.join([str(elem) for elem in messages[-self.chat_memory:]])
        json_obj = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "text": conv_string
        }
        r = requests.post(self.URL, json=json_obj)
        response = r.json()['text']
        if len(response) > 128:
            response = response[0:128]
        return response

    def shutdown(self):
        os.system("docker container kill {}".format(self.emely_id))
        time.sleep(5)


class Emely04(AbstractAgent):
    def __init__(self, agent_id, role='Other agent'):
        AbstractAgent.__init__(self, agent_id=agent_id, role=role)
        self.URL = "http://localhost:8080/inference"
        self.chat_memory = 6
        self.emely_id = "emely04"

    def setup(self):
        success = os.system("docker container restart {}".format(self.emely_id, self.emely_id))
        if success != 0:
            os.system("docker run --name {} -d -p 8080:8080 {}".format(self.emely_id, self.emely_id))
        time.sleep(5)

    def act(self, messages):
        # Inputs the conversation array and outputs a response from Emely
        conv_string = '\n'.join([str(elem) for elem in messages[-self.chat_memory:]])
        json_obj = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "text": conv_string
        }
        r = requests.post(self.URL, json=json_obj)
        response = r.json()['text']
        if len(response) > 128:
            response = response[0:128]
        return response

    def shutdown(self):
        os.system("docker container kill {}".format(self.emely_id))
        time.sleep(5)


class Emely05(AbstractAgent):
    def __init__(self, agent_id, role='Other agent'):
        AbstractAgent.__init__(self, agent_id=agent_id, role=role)
        self.URL = "http://localhost:8080/inference"
        self.chat_memory = 6
        self.emely_id = "emely05"

    def setup(self):
        success = os.system("docker container restart {}".format(self.emely_id, self.emely_id))
        if success != 0:
            os.system("docker run --name {} -d -p 8080:8080 {}".format(self.emely_id, self.emely_id))
        time.sleep(5)

    def act(self, messages):
        # Inputs the conversation array and outputs a response from Emely
        conv_string = '\n'.join([str(elem) for elem in messages[-self.chat_memory:]])
        json_obj = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "text": conv_string
        }
        r = requests.post(self.URL, json=json_obj)
        response = r.json()['text']
        if len(response) > 128:
            response = response[0:128]
        return response

    def shutdown(self):
        os.system("docker container kill {}".format(self.emely_id))
        time.sleep(5)


""" The conversational agents that are currently implemented. This dict is used for interpreting CLI arguments and from
that instantiate conversational agents. """
available_agents = {
    'human': Human,
    'blenderbot90m': BlenderBot90M,
    'blenderbot400m': BlenderBot400M,
    'emely02': Emely02,
    'emely03': Emely03,
    'emely04': Emely04,
    'emely05': Emely05
}


def load_conv_agent(agents, role='Other agent'):
    """ Method used for interpreting the CLI argument string and return instantiated conv_agents. """
    agents = agents.lower()
    agents = agents.split(',')
    list_conv_agents = []
    for agent in agents:
        list_conv_agents.append(available_agents[agent](agent_id=agent, role=role))
    return list_conv_agents
