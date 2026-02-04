import faiss
import numpy as np
import json
import pickle
import os
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from models import Disease

class AgriKnowledgeBase:
    def __init__(self, data_path: str = None):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.diseases_map = {}
        self.index = None
        self.disease_texts = []
        self.index_path = "faiss_index"
        
        # Set default data path if not provided
        if data_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(current_dir, "data", "knowledge_data.json")
        
        print(f"🔍 Looking for data at: {data_path}")
        
        # Try to load existing index first
        if not self.load_index():
            # If no index exists, load data and create new index
            self.load_data(data_path)
    
    def load_data(self, data_path: str):
        """Load disease data and create FAISS index"""
        try:
            print(f"📂 Loading data from: {data_path}")
            
            # Check if file exists
            if not os.path.exists(data_path):
                # Create default data if file doesn't exist
                self.create_sample_data(data_path)
            
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.disease_texts = []
            texts_for_embedding = []
            
            for disease in data['diseases']:
                # Create comprehensive document for embedding
                doc_text = f"""
                Crop: {disease['crop']}
                Disease: {disease['disease_name']}
                Description: {disease['description']}
                Causes: {disease['causes']}
                Symptoms: {disease['symptoms']}
                Solution: {disease['solution']}
                Prevention: {disease['prevention']}
                Pesticides: {', '.join([p['name'] for p in disease['pesticides']])}
                """
                
                self.disease_texts.append({
                    'text': doc_text,
                    'disease_id': disease['id']
                })
                texts_for_embedding.append(doc_text)
                
                # Store in map for quick retrieval
                self.diseases_map[disease['id']] = Disease(**disease)
            
            # Create embeddings and FAISS index
            if texts_for_embedding:
                print("🔄 Creating embeddings...")
                embeddings = self.model.encode(texts_for_embedding)
                
                # Create FAISS index
                dimension = embeddings.shape[1]
                self.index = faiss.IndexFlatIP(dimension)  # Using inner product for cosine similarity
                
                # Normalize vectors for cosine similarity
                faiss.normalize_L2(embeddings)
                self.index.add(embeddings)
                
                # Save index and metadata
                self.save_index()
                
                print(f"✅ Loaded {len(texts_for_embedding)} disease records into FAISS database")
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
    
    def create_sample_data(self, data_path: str):
        """Create sample data if file doesn't exist"""
        print("📝 Creating sample knowledge data...")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        
        sample_data = {
            "diseases": [
                {
                    "id": "1",
                    "disease_name": "Apple Scab",
                    "crop": "Apple",
                    "description": "Fungal disease causing dark, scabby lesions on apple leaves and fruit.",
                    "causes": "Caused by the fungus Venturia inaequalis; thrives in cool and wet spring weather.",
                    "symptoms": "Olive-green to black spots on leaves, scabby lesions on fruits",
                    "solution": "Remove infected leaves, prune trees for airflow, and spray with fungicides.",
                    "prevention": "Apply fungicides in early spring, maintain tree hygiene",
                    "pesticides": [
                        {
                            "name": "Mancozeb 75% WP",
                            "url": "https://www.indiamart.com/proddetail/mancozeb-75-wp-21089662191.html"
                        },
                        {
                            "name": "Captan Fungicide",
                            "url": "https://www.amazon.in/Captan-Fungicide-AgroChemicals/dp/B08L5V2J8M"
                        }
                    ]
                },
                {
                    "id": "2",
                    "disease_name": "Late Blight",
                    "crop": "Potato",
                    "description": "Causes dark lesions on leaves and tubers, leading to decay.",
                    "causes": "Caused by Phytophthora infestans; spreads fast in cool, moist weather.",
                    "symptoms": "Water-soaked lesions on leaves, white mold, tuber rot",
                    "solution": "Destroy infected plants, rotate crops, and use Metalaxyl fungicide.",
                    "prevention": "Use certified seed potatoes, avoid overhead irrigation",
                    "pesticides": [
                        {
                            "name": "Metalaxyl 8% + Mancozeb 64%",
                            "url": "https://www.indiamart.com/proddetail/metalaxyl-mancozeb-19693725848.html"
                        }
                    ]
                },
                {
                    "id": "3",
                    "disease_name": "Black Rot",
                    "crop": "Grape",
                    "description": "Dark brown spots on leaves and black shriveled grapes.",
                    "causes": "Caused by the fungus Guignardia bidwellii during humid conditions.",
                    "symptoms": "Dark brown spots on leaves, black shriveled grapes, cankers on stems",
                    "solution": "Prune and remove infected vines, and spray with Copper fungicide.",
                    "prevention": "Proper pruning, avoid overhead watering, remove infected plant parts",
                    "pesticides": [
                        {
                            "name": "Copper Oxychloride",
                            "url": "https://www.indiamart.com/proddetail/copper-oxychloride-18892304388.html"
                        }
                    ]
                },
                {
                    "id": "4",
                    "disease_name": "Powdery Mildew",
                    "crop": "Wheat",
                    "description": "White powdery growth on leaves and stems, reducing photosynthesis.",
                    "causes": "Caused by Blumeria graminis fungus in humid conditions with moderate temperatures.",
                    "symptoms": "White powdery spots on leaves, yellowing leaves, stunted growth",
                    "solution": "Apply sulfur-based fungicides, ensure proper spacing between plants.",
                    "prevention": "Plant resistant varieties, avoid excessive nitrogen fertilization",
                    "pesticides": [
                        {
                            "name": "Sulfur Dust",
                            "url": "https://www.indiamart.com/proddetail/sulfur-dust-21574236488.html"
                        },
                        {
                            "name": "Tebuconazole Fungicide",
                            "url": "https://www.indiamart.com/proddetail/tebuconazole-fungicide-22651400773.html"
                        }
                    ]
                },
                {
                    "id": "5",
                    "disease_name": "Bacterial Blight",
                    "crop": "Rice",
                    "description": "Water-soaked lesions that turn yellow and then white on rice leaves.",
                    "causes": "Caused by Xanthomonas oryzae bacteria, spreads through water and infected seeds.",
                    "symptoms": "Water-soaked lesions, yellowing leaves, white streaks, yield reduction",
                    "solution": "Use certified seeds, apply copper-based bactericides.",
                    "prevention": "Avoid flooded conditions, practice crop rotation",
                    "pesticides": [
                        {
                            "name": "Copper Hydroxide",
                            "url": "https://www.indiamart.com/proddetail/copper-hydroxide-21963596762.html"
                        },
                        {
                            "name": "Streptomycin Sulfate",
                            "url": "https://www.indiamart.com/proddetail/streptomycin-sulfate-22874548930.html"
                        }
                    ]
                }
            ]
        }
        
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created sample data at: {data_path}")
    
    def save_index(self):
        """Save FAISS index and metadata"""
        try:
            if self.index:
                faiss.write_index(self.index, f"{self.index_path}.faiss")
                with open(f"{self.index_path}_meta.pkl", 'wb') as f:
                    pickle.dump({
                        'disease_texts': self.disease_texts,
                        'diseases_map': self.diseases_map
                    }, f)
                print("✅ FAISS index saved successfully")
        except Exception as e:
            print(f"❌ Error saving index: {e}")
    
    def load_index(self):
        """Load FAISS index and metadata if exists"""
        try:
            if os.path.exists(f"{self.index_path}.faiss") and os.path.exists(f"{self.index_path}_meta.pkl"):
                print("📥 Loading existing FAISS index...")
                self.index = faiss.read_index(f"{self.index_path}.faiss")
                with open(f"{self.index_path}_meta.pkl", 'rb') as f:
                    data = pickle.load(f)
                    self.disease_texts = data['disease_texts']
                    self.diseases_map = data['diseases_map']
                print("✅ Loaded existing FAISS index")
                return True
        except Exception as e:
            print(f"❌ Error loading index: {e}")
        return False
    
    def search_diseases(self, query: str, n_results: int = 3) -> List[Disease]:
        """Search for diseases based on query using semantic search"""
        try:
            if not self.index:
                print("❌ No FAISS index available")
                return []
            
            print(f"🔍 Searching for: '{query}'")
            
            # Encode query
            query_embedding = self.model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search
            distances, indices = self.index.search(query_embedding, n_results)
            
            found_diseases = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.disease_texts) and idx >= 0:
                    disease_id = self.disease_texts[idx]['disease_id']
                    if disease_id in self.diseases_map:
                        found_diseases.append(self.diseases_map[disease_id])
            
            print(f"✅ Found {len(found_diseases)} relevant diseases")
            return found_diseases
            
        except Exception as e:
            print(f"❌ Error searching diseases: {e}")
            return []
    
    def get_all_diseases(self) -> List[Disease]:
        """Get all diseases in the database"""
        return list(self.diseases_map.values())

# Global instance
knowledge_base = AgriKnowledgeBase()
