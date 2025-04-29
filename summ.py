# Import modules
import pandas as pd
import string
import nltk
import networkx as nx
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

# Download data NLTK (sekali saja)
nltk.download('punkt')
nltk.download('stopwords')

# Fungsi ringkasan + keywords
def summarize_texts(article_text, num_keywords=20):
    artikel= article_text
    lines = artikel.split('\n')
    cleaned_lines = []

    #Untuk menghapis bagian yang tidak digunakan atau after titik
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped[-1] in ['.', '!', '?']:
            continue
        cleaned_lines.append(stripped)

    cleaned_artikel = ' '.join(cleaned_lines)
    text = cleaned_artikel

    sentences_raw = sent_tokenize(text)

    sentences = [sentence.lower() for sentence in sentences_raw]
    words_per_sentence = [word_tokenize(sentence) for sentence in sentences]
    words_cleaned = [
        [word for word in words if word not in string.punctuation and word.isalpha()]
        for words in words_per_sentence
    ]
    stop_words = set(stopwords.words('indonesian'))

    words_cleaned = [
        [word for word in words if word not in string.punctuation and word.isalpha() and word.lower() not in stop_words]
        for words in words_per_sentence
    ]
    unique_words = sorted(set(word for sentence in words_cleaned for word in sentence))
    word_counts_per_sentence = [len(words) for words in words_cleaned]



    #
    cleaned_sentences = [' '.join(words) for words in words_cleaned if words]
    word_counts = {word: [0] * len(sentences) for word in unique_words}

    for i, sentence in enumerate(words_cleaned):
        word_freq = Counter(sentence)
        for word, count in word_freq.items():
            word_counts[word][i] = count

    df_wordcount = pd.DataFrame(word_counts, index=[f"Sentence {i+1}" for i in range(len(sentences))]).T
    df_wordcount.columns.name = "Word"

    #
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(cleaned_sentences)
    vectorizer.get_feature_names_out()
    tfidf_matrix.toarray()
    cosine_sim = cosine_similarity(tfidf_matrix)
    df_sim = pd.DataFrame(cosine_sim, index=[f"{i+1}" for i in range(len(cleaned_sentences))],
                        columns=[f"{i+1}" for i in range(len(cleaned_sentences))])
    graph = nx.Graph()

    # Menambahkan node
    for i, cleaned_sentence in enumerate(cleaned_sentences):
        graph.add_node(i, text=cleaned_sentences)

    # Menambahkan edge berdasarkan Cosine Similarity (tidak termasuk diagonal)
    for i in range(len(cleaned_sentences)):
        for j in range(i+1, len(cleaned_sentences)):
            if cosine_sim[i, j] > 0:
                graph.add_edge(i, j, weight=cosine_sim[i, j])

    # Implementasi TextRank --> menggunakan PageRank dengan damping factor 0.85
    ranks = nx.pagerank(graph, alpha=0.85, max_iter=100, tol=0.000001)

    # Ranking kalimat
    ranked_sentences = sorted(ranks.items(), key=lambda x: x[1], reverse=True)
    percentage_30 = 0.3
    num_top_sentences = int(len(ranked_sentences) * percentage_30)
    top_sentences = [sentences_raw[index] for index, score in ranked_sentences[:num_top_sentences]]

    paragraph = ' '.join(top_sentences)

    # Sekarang cari keywords
    # Tokenisasi ringkasan
    summary = paragraph
    summary_tokens = word_tokenize(summary.lower())
    summary_tokens = [word for word in summary_tokens if word.isalpha() and word not in stop_words]

    # Buat graph untuk words
    word_graph = nx.Graph()
    for i in range(len(summary_tokens)):
        for j in range(i + 1, len(summary_tokens)):
            if summary_tokens[i] != summary_tokens[j]:
                word_graph.add_edge(summary_tokens[i], summary_tokens[j])

    word_ranks = nx.pagerank(word_graph, alpha=0.85, max_iter=100, tol=0.000001)
    ranked_words = sorted(word_ranks.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, _ in ranked_words[:num_keywords]]

    return paragraph, keywords