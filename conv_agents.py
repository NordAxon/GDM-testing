import abc

from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration, pipeline, AutoModelForSeq2SeqLM, \
    AutoTokenizer

from conversation import Message


class AbstractAgent(abc.ABC):
    """Abstract base class that defines the interface for a conversational agent."""

    def __init__(self):
        pass

    @abc.abstractmethod
    def act(self) -> Message:
        "Define how to get a reply from the agent"
        pass


# ------- Different conversational agents implemented

# Conversational agent where one human is involved
class Human():
    def __init__(self):
        pass

    def act(self):
        response = input("You: ")
        return response


# BlenderBot's 400M model as a conversational agent
class BlenderBot400M:
    def __init__(self):
        self.name = 'facebook/blenderbot-400M-distill'
        self.model = BlenderbotForConditionalGeneration.from_pretrained(self.name)
        self.tokenizer = BlenderbotTokenizer.from_pretrained(self.name)
        self.memory_chatbot = 3

    def act(self, conversation):
        conv_string = self.__array2blenderstring(conversation[-self.memory_chatbot:])
        if len(conv_string) > 128:
            conv_string = conv_string[-128:]
        inputs = self.tokenizer([conv_string], return_tensors='pt')
        reply_ids = self.model.generate(**inputs)
        response = self.tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
        return response

    def __array2blenderstring(self, conversation):
        conv_string = ' '.join([str(elem) + '</s> <s>' for elem in conversation])
        conv_string = conv_string[:len(conv_string) - 8]
        return conv_string


# Blenderbot's 90M model as a conversational agent
class BlenderBot90M:

    def __init__(self):
        self.name = 'facebook/blenderbot_small-90M'
        self.model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot_small-90M")
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot_small-90M")

    def act(self, conversation):
        conv_string = '.'.join(elem for elem in conversation[-1:])
        inputs = self.tokenizer([conv_string], return_tensors='pt')
        reply_ids = self.model.generate(**inputs)
        response = self.tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
        return response


available_agents = {
    'human': Human,
    'blenderbot90m': BlenderBot90M,
    'blenderbot400m': BlenderBot400M
}


def load_conv_agent(agents):
    agents = agents.lower()
    agents = agents.split(',')
    list_conv_agents = []
    for agent in agents:
        list_conv_agents.append(available_agents[agent]())
    return list_conv_agents
