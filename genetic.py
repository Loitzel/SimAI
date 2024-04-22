import random
from API import TopicExtractor
from belief import Belief
from enviroment import Environment
from message import Message
from reporter import Reporter
from topics import Topics


def get_notified_agents_count():
    reporter = Reporter()
    return len(reporter._notified_agents)

def generate_random_messages(num_messages, num_topics_per_message):
    population = []
    for _ in range(num_messages):
        topics = Topics.select_random_topics(num_topics_per_message)
        beliefs = [Belief(topic.value, random.randint(-2, 2)) for topic in topics]
        message = Message(strength=5, beliefs=beliefs)  # Fuerza inicial 5
        population.append(message)
    return population

def generate_messages_from_prompts(prompts):
    extractor = TopicExtractor()
    population = []
    for prompt in prompts:
        topics = extractor.extract_topics(prompt)
        beliefs = [Belief(topic[0], topic[1]) for topic in topics]
        message = Message(strength=5, beliefs=beliefs)
        population.append(message)
    return population

def generate_messages_with_specific_topics(topics, num_messages):
    population = []
    for _ in range(num_messages):
        beliefs = [Belief(topic.value, random.randint(-2, 2)) for topic in topics]
        message = Message(strength=5, beliefs=beliefs)
        population.append(message)
    return population

def evaluate_population(population, initial_agents):
    environment = Environment.get_instance()
    for message in population:
        reporter = Reporter()
        # Ejecutar la simulación para cada mensaje
        environment.run_simulation(message, initial_agents)
        num_notified_agents = get_notified_agents_count()
        reporter = Reporter()
        reporter.Reset()

        # Almacenar el resultado (cantidad de agentes notificados)
        message.result = num_notified_agents
        return num_notified_agents

def select_parents(population, num_parents):
    """Selecciona los padres con base en el atributo 'result' de los mensajes."""
    # Ordenar la población por el atributo 'result' (de mayor a menor)
    population.sort(key=lambda message: message.result, reverse=True)

    # Seleccionar los primeros 'num_parents' mensajes como padres
    parents = population[:num_parents]
    return parents

def crossover(parent1, parent2):
    """Realiza el cruce entre dos padres y combina creencias."""
    beliefs1 = parent1.beliefs
    beliefs2 = parent2.beliefs

    # Encontrar tópicos comunes y promediar opiniones
    common_topics = set(belief.topic for belief in beliefs1) & set(belief.topic for belief in beliefs2)
    child_beliefs = []
    for topic in common_topics:
        opinion1 = next(belief.opinion for belief in beliefs1 if belief.topic == topic)
        opinion2 = next(belief.opinion for belief in beliefs2 if belief.topic == topic)
        average_opinion = (opinion1 + opinion2) / 2
        rounded_opinion = round(average_opinion)  # Redondear al entero más cercano
        child_beliefs.append(Belief(topic, rounded_opinion))

    # Agregar tópicos no comunes de los padres
    for belief in beliefs1 + beliefs2:
        if belief.topic not in common_topics:
            child_beliefs.append(belief)

    # Limitar el número de creencias a 5 al azar
    random.shuffle(child_beliefs)
    child_beliefs = child_beliefs[:3]

    # Crear un nuevo mensaje con las creencias combinadas
    child_message = Message(strength=5, beliefs=child_beliefs)

    return child_message

def mutate(message, mutation_rate=0.1):
    """Aplica mutaciones al mensaje."""
    mutated_beliefs = []
    for belief in message.beliefs:
        if random.random() < mutation_rate:
            # Decidir si modificar el valor o agregar un nuevo topic
            if random.random() < 0.5:
                # Modificar el valor del topic
                new_opinion = random.randint(-2, 2)
                mutated_beliefs.append(Belief(belief.topic, new_opinion))
            else:
                # Agregar un nuevo topic
                new_topic = Topics.select_random_topics(1)[0].value
                new_opinion = random.randint(-2, 2)
                mutated_beliefs.append(Belief(new_topic, new_opinion))
        else:
            # Mantener la creencia sin cambios
            mutated_beliefs.append(belief)

    # Crear un nuevo mensaje con las creencias mutadas
    mutated_message = Message(strength=message.strength, beliefs=mutated_beliefs)
    return mutated_message

def reproduce(parent1, parent2, global_best, mutation_rate=0.1):
    """Realiza el cruce y la mutación para crear un nuevo hijo."""
    if global_best is None:
        child_message = crossover(parent1, parent2)
    else:
        child_message = crossover(parent1, global_best)

    mutated_child = mutate(child_message, mutation_rate)
    return mutated_child

def genetic_algorithm(population_size, num_parents, num_generations, mutation_rate, initial_agents):
    # Generar la población inicial
    population = generate_random_messages(population_size, num_topics_per_message=5)
    global_best = (None, 0)
    evolution_list = []

    for generation in range(num_generations):
        # Evaluar la población
        evaluate_population(population, initial_agents)

        # Seleccionar padres
        parents = select_parents(population, num_parents)

        # Crear nueva generación
        new_population = []
        for _ in range(population_size):
            # Seleccionar padres aleatoriamente
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            # Reproducir (cruce y mutación)
            child = reproduce(parent1, parent2, global_best[0], mutation_rate)

            # Agregar el hijo a la nueva población
            new_population.append(child)

            # Imprimir información de la generación
        best_message = max(population, key=lambda message: message.result)
        print(best_message.result)
        evolution_list.append(best_message.result)


        if global_best[1] < best_message.result:
            global_best = (best_message, best_message.result)

        # Reemplazar la población actual con la nueva generación
        population = new_population

    return global_best[0], evolution_list