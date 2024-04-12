import pandas as pd
from query import infix_to_postfix
from Stack import Stack

class BooleanModel(object):

    def __init__(self, inverted_index_file, meta_file):
        # Load inverted index CSV file
        self.inverted_index_df = pd.read_csv(inverted_index_file)
        # Load meta file CSV
        self.meta_file_df = pd.read_csv(meta_file)

    def query(self, query):
        if len(query.split()) == 1:
            # Single term query
            matching_docs = self.get_matching_docs(query)
        else:
            # Boolean expression query
            postfix_query = infix_to_postfix(query.split())
            matching_docs = self.evaluate_query(postfix_query)
        return matching_docs

    def get_matching_docs(self, term):
        term = term.lower()
        if term in self.inverted_index_df['Keyword'].values:
            posting_list = self.inverted_index_df.loc[self.inverted_index_df['Keyword'] == term, 'Posting List'].iloc[0]
            doc_ids = [int(doc_id) for doc_id in posting_list.split('-') if doc_id.strip()]
            matching_docs = self.meta_file_df[self.meta_file_df.index.isin(doc_ids)].to_dict(orient='records')
            return matching_docs
        else:
            return []

    def evaluate_query(self, query):

        stack = Stack()

        for token in query:
            if token not in ['&', '|', '~']:
                stack.push(self.get_matching_docs(token))
            else:
                if token == '&':
                    right = stack.pop()
                    left = stack.pop()
                    result = self.perform_and(left, right)
                    stack.push(result)
                elif token == '|':
                    right = stack.pop()
                    left = stack.pop()
                    result = self.perform_or(left, right)
                    stack.push(result)
                elif token == '~':
                    operand = stack.pop()
                    result = self.perform_not(operand)
                    stack.push(result)

        return stack.pop()

    def perform_and(self, left, right):
        merged_docs = []
        for doc in left:
            if doc in right:
                merged_docs.append(doc)
        return merged_docs

    def perform_or(self, left, right):
        merged_docs = []
        for doc in left + right:
            if doc not in merged_docs:
                merged_docs.append(doc)
        return merged_docs

    def perform_not(self, operand):
        all_doc_ids = set(self.meta_file_df['ID'])
        operand_ids = set(doc['ID'] for doc in operand)
        result_ids = all_doc_ids - operand_ids
        result = [doc for doc in self.meta_file_df.to_dict(orient='records') if doc['ID'] in result_ids]
        return result



