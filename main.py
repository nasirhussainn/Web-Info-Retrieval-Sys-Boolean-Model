from flask import Flask, render_template, request, jsonify
from BooleanModel import BooleanModel


app = Flask(__name__)
boolean_model = BooleanModel("inverted_index.csv", "meta_file.csv")

@app.route('/', methods=['GET', 'POST'])
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        relevant_documents = process_query(query)
        return render_template('index.html', query=query, relevant_documents=relevant_documents)
    return render_template('index.html', query=None, relevant_documents=None)

@app.route('/load_more', methods=['GET'])
def load_more():
    return jsonify()

def process_query(query):
    matching_docs = boolean_model.query(query)
    return matching_docs

if __name__ == '__main__':
    app.run(debug=True)
