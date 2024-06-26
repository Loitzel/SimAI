from abc import ABC, abstractmethod
from belief import Belief
from communication_rules import CommunicationRule
from message import Message
from reporter import Reporter
from beliefs_rule import BeliefRule
from typing import List
class AgentInterface(ABC):
    """Abstract base class for agent interfaces."""
    @abstractmethod
    def receive_message(self, message):
        """Receives a message and triggers the agent's deliberation."""
        pass

    @abstractmethod
    def deliberate(self, message, agreement, interest, common_topics):
        """Deliberates on whether to transmit, alter, or not transmit the message."""
        pass

    @abstractmethod
    def execute_action(self, message):
        """Executes the action determined by the deliberation."""
        pass
    
    @abstractmethod
    def to_dict(self):
        pass
    


class Agent(AgentInterface):
    """Agent class implementing the AgentInterface."""
    def __init__(self, beliefs, decision_rules, beliefs_rules:List[BeliefRule], communication_rule : CommunicationRule,  neighbors, name=''):
        """Initializes the agent with beliefs and decision rules."""
        self.name = name
        self.beliefs = beliefs  # Agent's beliefs
        self.decision_rules = decision_rules  # Decision rules for deliberation
        self.beliefs_rules = beliefs_rules
        self.neighbors = neighbors  # Add neighbors attribute
        self.communication_rule = communication_rule
        self.neighbors_beliefs_hypothesis = {}


    def to_dict(self):
        return { 'name' : self.name,
        'beliefs' : [str(belief) for belief in self.beliefs],  # Agent's beliefs
        'neighbors' : self.neighbors}  # Add neighbors attribute
        
    def receive_message(self, original_message: Message):
        """Receives a message and initiates the deliberation process."""
        self.updateNeighborsBeliefs(original_message)

        reporter = Reporter()
        reporter.reportAgent(self.name)

        message = original_message.clone()

        message_beliefs = message.get_beliefs_as_dict()
        agent_beliefs = {belief.topic: belief.opinion for belief in self.beliefs}
        agreement_with_message, interest_on_message, common_topics = self.calculate_agreement_and_interest(agent_beliefs, message_beliefs)
        

        while True:
            change = False
            for rule in self.beliefs_rules:
                change = change or rule.change(self, interest_on_message, agreement_with_message, message)
            if not change:
                break

        self.deliberate(message, agreement_with_message, interest_on_message, common_topics)

    def deliberate(self, message : Message, agreement, interest, common_topics):
        """Deliberates on whether to transmit, alter, or not transmit the message."""
        new_message = None
        agent_report = ''
        for rule in self.decision_rules:
            decision = rule.decide(self.beliefs, interest, agreement, message)
            if decision:
                new_message = rule.alter(self.beliefs, common_topics, interest, agreement, message)
                break
        
        if new_message is not None:
            for neighbor in self.neighbors:
                if neighbor == message.source:
                    continue
                
                neighbor_beliefs = self.neighbors_beliefs_hypothesis[neighbor].getBeliefs()

                if self.communication_rule.communicate(interest, message.beliefs, 
                                                    neighbor_beliefs, message):
                    new_message = new_message.clone()
                    new_message.source = self.name
                    new_message.destination = neighbor
                    agent_report = rule.report(self.name, new_message)
                    self.execute_action(new_message, agent_report)
        
    def execute_action(self, message, agent_report):
        
        from enviroment import Environment
        environment = Environment()  # Access the singleton Environment
        
        reporter = Reporter()
        reporter.report(agent_report)
        reporter.reportAgent(self.name)
        environment.send_message(message)
        
    def calculate_agreement_and_interest(self, agent_beliefs, message_beliefs):
        """Calculates agreement and interest between agent beliefs and message beliefs."""
        common_topics = set(agent_beliefs.keys()) & set(message_beliefs.keys())

        agreement_scores = {}

        for topic in common_topics:
            total_agreement = abs(agent_beliefs[topic] - message_beliefs[topic])
            max_possible_agreement = 2  # Maximum agreement possible on a single topic (both opinions are +2 or -2)

            agreement_score = 1 - (total_agreement / max_possible_agreement)  # Convert difference to agreement score
            agreement_scores[topic] = agreement_score

        return agreement_scores, len(common_topics), common_topics
    
    def updateNeighborsBeliefs(self, message : Message):
        neighbor = message.source

        if neighbor is None:
            return
        
        for belief in message.beliefs:
            self.neighbors_beliefs_hypothesis[neighbor].addBeliefHypothesis(belief)

        self.neighbors_beliefs_hypothesis[neighbor].tick()

    def instantiate_neighbor_hypothesis(self):
        for neighbor in self.neighbors:
            self.neighbors_beliefs_hypothesis[neighbor] = BeliefsHypothesisList()

    def clone(self):
        clone = Agent(self.beliefs, self.decision_rules, self.beliefs_rules, self.communication_rule, self.neighbors, self.name)
        clone.neighbors_beliefs_hypothesis = self.neighbors_beliefs_hypothesis
        return clone
    
    def __str__(self):
        return f'{self.name} \n{[(belief.topic, belief.opinion) for belief in self.beliefs]}'
    
class NeighborBeliefHypothesis():
    def __init__(self, belief, age = 3):
        self.belief = belief
        self.age = age

class BeliefsHypothesisList():

    def __init__(self):
        self.hypothesis = []

    def addBeliefHypothesis(self, belief : Belief):
        
        for element in self.hypothesis:
            if element.belief.topic == belief.topic:
                element.belief.opinion += belief.opinion
                element.age = 3
                return
        
        self.hypothesis.append(NeighborBeliefHypothesis(belief.clone()))

    def getBeliefs(self):
        beliefs = []
        for element in self.hypothesis:
            beliefs.append(element.belief)
        
        return beliefs
    
    def tick(self):
        for element in self.hypothesis:
            element.age -= 1
            if element.age <= 0:
                self.hypothesis.remove(element)
