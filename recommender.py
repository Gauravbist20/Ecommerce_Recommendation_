
import math
import re
from collections import Counter


def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


def tfidf_documents(documents):
    tokenized = [tokenize(doc) for doc in documents]
    total = len(tokenized)

    document_frequency = Counter()

    for words in tokenized:
        document_frequency.update(set(words))

    vectors = []

    for words in tokenized:
        counts = Counter(words)
        vector = {}

        for word, count in counts.items():
            tf = count / len(words) if words else 0
            idf = math.log(
                (total + 1) / (document_frequency[word] + 1)
            ) + 1

            vector[word] = tf * idf

        vectors.append(vector)

    return vectors


def cosine_similarity(vector1, vector2):
    common = set(vector1) & set(vector2)

    dot_product = sum(
        vector1[word] * vector2[word]
        for word in common
    )

    magnitude1 = math.sqrt(
        sum(value ** 2 for value in vector1.values())
    )

    magnitude2 = math.sqrt(
        sum(value ** 2 for value in vector2.values())
    )

    if magnitude1 == 0 or magnitude2 == 0:
        return 0

    return dot_product / (magnitude1 * magnitude2)


def recommend_products(products, selected_id, limit=5):
    documents = [
        product[1] + " " + product[2] + " " + product[4]
        for product in products
    ]

    vectors = tfidf_documents(documents)

    selected_index = next(
        (
            i for i, product in enumerate(products)
            if product[0] == selected_id
        ),
        None
    )

    if selected_index is None:
        return []

    scores = []

    for i, product in enumerate(products):
        if i != selected_index:
            score = cosine_similarity(
                vectors[selected_index],
                vectors[i]
            )

            scores.append((score, product))

    scores.sort(key=lambda item: item[0], reverse=True)

    return [
        {
            "product": product,
            "score": round(score * 100, 1)
        }
        for score, product in scores[:limit]
    ]
