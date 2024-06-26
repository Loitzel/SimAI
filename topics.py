from enum import Enum
import random

class Topics(Enum):
    """Enum representing different topics."""
    HEALTH_AND_WELLNESS = "Health and wellness"
    TECHNOLOGY_AND_SOCIETY = "Technology and society"
    EDUCATION_AND_LEARNING = "Education and learning"
    ENVIRONMENT_AND_SUSTAINABILITY = "Environment and sustainability"
    CULTURE_AND_TRADITIONS = "Culture and traditions"
    ECONOMY_AND_FINANCE = "Economy and finance"
    POLITICS_AND_GOVERNMENT = "Politics and government"
    SCIENCE_AND_DISCOVERIES = "Science and discoveries"
    ART_AND_CREATIVITY = "Art and creativity"
    WORK_AND_CAREER = "Work and career"
    LEISURE_AND_ENTERTAINMENT = "Leisure and entertainment"
    TRAVEL_AND_TOURISM = "Travel and tourism"
    FOOD_AND_NUTRITION = "Food and nutrition"
    SPORTS_AND_PHYSICAL_ACTIVITY = "Sports and physical activity"
    RELIGION_AND_SPIRITUALITY = "Religion and spirituality"
    FASHION_AND_STYLE = "Fashion and style"
    HISTORY_AND_HERITAGE = "History and heritage"
    TECHNOLOGY_AND_GADGETS = "Technology and gadgets"
    TRANSPORTATION_AND_MOBILITY = "Transportation and mobility"
    JUSTICE_AND_HUMAN_RIGHTS = "Justice and human rights"
    COMMUNICATION_AND_MEDIA = "Communication and media"
    COMMUNITY_AND_SOCIETY = "Community and society"
    HOME_AND_DOMESTIC_LIFE = "Home and domestic life"
    SECURITY_AND_PROTECTION = "Security and protection"
    
    def select_random_topics(num_topics):
        """Selects a random set of topics from the Topics enum.

        Args:
            num_topics: The number of topics to select.

        Returns:
            A list of randomly chosen Topics enum members.
        """
        all_topics = list(Topics)
        random.shuffle(all_topics)  # Shuffle the list for random selection
        return all_topics[:num_topics]

