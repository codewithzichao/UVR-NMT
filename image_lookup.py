from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import random
import pickle
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('--stopwords_dir', default="data/stopwords-en.txt", help='path of the stopwords-en.txt')
parser.add_argument('--src_dict_dir', default="data/src_dict_en2de.txt", help='path of the source dict of en2de dataset')
parser.add_argument('--src_en_dir', default="data/multi30k_train_bpe.txt", help='path of the the segmented file for multi30k training set using the same bpe code with the nmt dataset (e.g., en2de)')
parser.add_argument('--image_dir', default="data/task1/image_splits/train.txt", help='path of the image_splits of training set of multi30k')
parser.add_argument('--cap2image_file', default="data/cap2image_en2de.pickle", help='output file for (topic) word to image id lookup table')
parser.add_argument('--seed', default=128, type=int, help='random seed')
parser.add_argument('--tfidf', default=8, type=int, help='tfidf topics')
parser.add_argument('--num_img', default=5, type=int, help='number of images')

args = parser.parse_args()
random.seed(args.seed)
np.random.seed(args.seed)

stopwords_dir = args.stopwords_dir
src_dict_dir = args.src_dict_dir
src_en_dir = args.src_en_dir
tfidf = args.tfidf
num_img = args.num_img
image_dir = args.image_dir

cap2image_file = args.cap2image_file

print("caption processing...")
total_img = 0

stop_words = []
if stopwords_dir:
    with open((stopwords_dir), "r") as data:
        for word in data:
            stop_words.append(word.strip())


src_dict = {}
with open((src_dict_dir), "r") as data:
    for line in data:
        word, idx = line.strip().split()
        src_dict[word] = int(idx)

cap2ids = {}  # caption dict
cap_sentences = []
cap_sentences_raw = []
with open((src_en_dir), "r") as data:
    for line in data:
        cap = line.strip()
        total_img += 1
        if stopwords_dir:
            wordsFiltered = []
            cap = cap.strip().split()
            for w in cap:
                if w not in stop_words:
                    wordsFiltered.append(w)
            cap = " ".join(wordsFiltered)
        cap_sentences.append(cap.split())
        cap_sentences_raw.append(cap)

n = tfidf
words, weight = None, None
if n > 0:
    print("tf-idf processing")
    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(vectorizer.fit_transform(cap_sentences_raw))
    words = vectorizer.get_feature_names() 
    weight = tfidf.toarray()

for idx, cap in enumerate(cap_sentences):
    if n > 0:
        w = weight[idx]
        loc = np.argsort(-w)
        top_words = []
        for i in range(n):
            if w[loc[i]] > 0.0:
                top_words.append(words[loc[i]])
        top_cap = []
        cap = cap
        for word in cap:
            if word.lower() in top_words:
                top_cap.append(word)
        cap = top_cap

    tokenized_cap = cap


    for cap in tokenized_cap:
        if cap not in stop_words and cap in src_dict:
            if src_dict[cap] not in cap2ids:
                cap2ids[src_dict[cap]] = [idx + 1]  # index 0 is used for placeholder
            else:
                cap_list = cap2ids[src_dict[cap]]
                cap_list.append(idx + 1)
                cap2ids[src_dict[cap]] = cap_list

for key, value in cap2ids.items():
    if len(value) < num_img:
        value.extend([0] * (num_img - len(value)))
        cap2ids[key] = value
    else:
        value = random.sample(value, num_img)
        cap2ids[key] = value

pickle.dump(cap2ids,open(cap2image_file,"wb"))

print("data process finished!")
print(len(cap2ids))
print(total_img)