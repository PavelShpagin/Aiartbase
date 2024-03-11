from sqlalchemy.orm import Session
from models import Category
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os

embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name="text-embedding-ada-002")
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection_categories = chroma_client.get_or_create_collection(name="Categories", embedding_function=embedding_function)

def create_categories(db: Session, category_names: list):
    for name in category_names:
        category = Category(name=name)
        db.add(category)
        db.commit()
        db.refresh(category)
        
        collection_categories.add(
            documents=[name],
            ids=[str(category.id)]
        )

if __name__ == "__main__":
    from database import SessionLocal  # Use your actual path to database

    # List of categories to seed
    categories = [
        "Anime",
        "Fantasy",
        "Abstract",
        "Science Fiction",
        "Space",
        "Cyberpunk",
        "Steampunk",
        "Underwater",
        "Apocalyptic",
        "Virtual Reality",
        "Alien Worlds",
        "Robotics",
        "Futuristic Cities",
        "Biomechanical",
        "Surrealism",
        "Dreamscapes",
        "Mythological Creatures",
        "Utopian Visions",
        "Dystopian Visions",
        "Interstellar",
        "Deep Space",
        "Time Travel",
        "Parallel Universes",
        "Quantum Realities",
        "Artificial Intelligence",
        "Digital Landscapes",
        "Augmented Reality",
        "Mystical Forests",
        "Magical Realism",
        "Neon Noir",
        "Post-Human",
        "Concept Art",
        "Character Design",
        "Creature Design",
        "Tech Noir",
        "Space Opera",
        "High Fantasy",
        "Dark Fantasy",
        "Historical Fantasy",
        "Prehistoric",
        "Ancient Civilizations",
        "Retrofuturism",
        "Nano Art",
        "Macro World",
        "Microbiology",
        "Genetic Art",
        "Psychedelic",
        "Therapeutic Art",
        "Mandala",
        "Zentangle",
        "Kinetic Art",
        "Optical Illusions",
        "3D Art",
        "Hyperrealism",
        "Matte Painting",
        "Landscape",
        "Seascape",
        "Cityscape",
        "Arctic Wonders",
        "Desert Mirage",
        "Jungle",
        "Mountainous",
        "Extraterrestrial Life",
        "Supernatural",
        "Cosmic Horror",
        "Gothic",
        "Medieval",
        "Renaissance",
        "Baroque",
        "Victorian",
        "Modernism",
        "Impressionism",
        "Cubism",
        "Expressionism",
        "Pointillism",
        "Fauvism",
        "Dadaism",
        "Pop Art",
        "Minimalism",
        "Abstract Expressionism",
        "Color Field",
        "Street Art",
        "Graffiti",
        "Digital Collage",
        "Conceptual Art",
        "Performance Art",
        "Installation Art",
        "Eco Art",
        "Political Art",
        "Comic Style",
        "Graphic Novel",
        "Manga",
        "Kawaii",
        "Chibi",
        "Steam Age",
        "Silicon Age",
        "Information Age",
        "Network Society",
        "Autonomous Art",
        "Generative Art",
        "Crypto Art",
        "Voxel Art",
        "Pixel Art",
        "Glitch Art"
    ]

    # Create a new database session
    db = SessionLocal()

    # Seed the categories
    create_categories(db, categories)

    # Close the session
    db.close()