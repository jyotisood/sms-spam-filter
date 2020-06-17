from flask import Flask,render_template,url_for,request, jsonify
import pandas as pd 
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import *
from sklearn.svm import *
import nltk
import re
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

app = Flask(__name__)
global Classifier
global Vectorizer
stop_words = nltk.corpus.stopwords.words('english')
porter = nltk.PorterStemmer()


def preprocess_data(data):
    data = str(data)
    cleaned = re.sub(r'\b[\w\-.]+?@\w+?\.\w{2,4}\b', 'emailaddr', data)
    cleaned = re.sub(r'(http[s]?\S+)|(\w+\.[A-Za-z]{2,4}\S*)', 'httpaddr',cleaned)
    cleaned = re.sub(r'£|\$', 'moneysymb', cleaned)
    cleaned = re.sub(r'\b(\+\d{1,2}\s)?\d?[\-(.]?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b','phonenumbr', cleaned)
    cleaned = re.sub(r'\d+(\.\d+)?', 'numbr', cleaned)
    cleaned = re.sub(r'[^\w\d\s]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'^\s+|\s+?$', '', cleaned.lower())
    return ' '.join(
        porter.stem(term) 
        for term in cleaned.split()
        if term not in set(stop_words)
    )

# load data
data = pd.read_csv('data/sms-spam-collection-dataset/spam.csv', encoding='latin-1')
train_data = data[:4400] # 4400 items
test_data = data[4400:] # 1172 items
preprocess_data(train_data)
preprocess_data(test_data)



# train model
Classifier = OneVsRestClassifier(SVC(kernel='linear', probability=True))
Vectorizer = TfidfVectorizer()
vectorize_text = Vectorizer.fit_transform(train_data.v2)
Classifier.fit(vectorize_text, train_data.v1)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/predict',methods=['POST'])
def predict():
	error = ''
	predict_proba = ''
	predict = ''
	if request.method == 'POST':
		message = request.form['message']
        
        
        
		try:
			if len(message) > 0:
				vectorize_message = Vectorizer.transform([preprocess_data(message)])
				predict = Classifier.predict(vectorize_message)[0]
				predict_proba = Classifier.predict_proba(vectorize_message).tolist()
			else:
				predict = 2
		except BaseException as inst:
			error = str(type(inst).__name__) + ' ' + str(inst)
	if (predict == 'ham'):
		predict = 1
	elif (predict == 'spam'):
		predict = 0
	return render_template('result.html', prediction = predict)

if __name__ == '__main__':
	app.run(debug=True, use_reloader=False)