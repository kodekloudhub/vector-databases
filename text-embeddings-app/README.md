# Text to Vector Converter

A simple Streamlit application that converts text to numerical vectors using different embedding methods.

## Features

- **TF-IDF Embeddings**: Traditional text vectorization method
- **Sentence Transformers**: AI-powered semantic embeddings
- **2D Visualization**: Interactive plots showing text relationships
- **CSV Export**: Download vector results

## Sample Inputs for Different Clustering Patterns

Here are three examples that demonstrate different clustering behaviors:

### Example 1: Tight Group (Food & Cooking)
```
I love cooking Italian food
Pizza is my favorite meal
Making pasta from scratch is fun
I enjoy baking bread
Cooking with fresh ingredients
Italian cuisine is delicious
Baking cookies with my kids
I love making homemade pizza
```
**Expected Result**: All texts will cluster very tightly together due to high vocabulary overlap.

### Example 2: Smaller Groups (Programming & Nature)
```
Python is a great programming language
Machine learning algorithms are fascinating
I love coding in Python
Artificial intelligence is the future
Data science requires programming skills
Python makes data analysis easy
Machine learning models need training data
Programming is like solving puzzles
Dogs are loyal companions
I love hiking in the mountains
Cats are independent pets
Nature is beautiful and peaceful
Birds sing in the morning
I enjoy walking in the forest
Pets bring joy to families
The mountains are majestic
```
**Expected Result**: Two distinct clusters - programming/tech texts and nature/animal texts.

### Example 3: Scattered/Outlier Texts
```
Quantum physics is fascinating
The weather is nice today
I need to buy groceries
Cooking is fun
Machine learning is interesting
Dogs are cute
The sky is blue
I love reading books
```
**Expected Result**: Texts will appear scattered with no clear clustering due to diverse, unrelated topics.

**Tip**: Try each example separately to see how different clustering patterns emerge in the visualization!

## Quick Start

### Using Docker (Recommended)

1. **Clean up existing Docker resources:**
```bash
# Stop and remove containers
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)

# Remove images
docker rmi $(docker images -q)

# Remove volumes (optional)
docker volume prune -f

# Remove networks (optional)
docker network prune -f

# Clean up everything (use with caution)
docker system prune -a -f
```

2. **Build and run:**
```bash
# Build the image
docker build -t text-embeddings-app .

# Run the container
docker run -p 8501:8501 text-embeddings-app
```

3. **Access the app:**
   - Open your browser and go to: http://localhost:8501

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the app:**
```bash
streamlit run app.py
```

## Usage

1. Choose an embedding method (TF-IDF or Sentence Transformers)
2. Enter text or use example texts
3. Click "Convert Text to Numbers"
4. View the 2D visualization and vector values
5. Download results as CSV

## Requirements

- Python 3.11+
- See `requirements.txt` for Python packages
- Docker (for containerized deployment)

## Project Structure

```
text-embeddings-app/
├── app.py                 # Main Streamlit application
├── embeddings/           # Embedding modules
│   ├── tfidf_embedder.py
│   └── transformer_embedder.py
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
└── README.md           # This file
```
