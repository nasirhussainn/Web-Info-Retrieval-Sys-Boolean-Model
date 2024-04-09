import pandas as pd
from query import infix_to_postfix
from Stack import Stack

class BooleanModel(object):
    """ Boolean model for unranked retrieval of information """

    def __init__(self, inverted_index_file, meta_file):
        # Load inverted index CSV file
        self.inverted_index_df = pd.read_csv(inverted_index_file)
        # Load meta file CSV
        self.meta_file_df = pd.read_csv(meta_file)

    def query(self, query):
        """Query the indexed documents using a boolean model

        :param query: valid boolean expression to search for
        :returns: list of dictionaries representing matching documents
        """
        if len(query.split()) == 1:
            # Single term query
            matching_docs = self.get_matching_docs(query)
        else:
            # Boolean expression query
            postfix_query = infix_to_postfix(query.split())
            matching_docs = self.evaluate_query(postfix_query)
        return matching_docs

    def get_matching_docs(self, term):
        """Get documents matching a single term"""
        term = term.lower()
        if term in self.inverted_index_df['Keyword'].values:
            posting_list = self.inverted_index_df.loc[self.inverted_index_df['Keyword'] == term, 'Posting List'].iloc[0]
            doc_ids = [int(doc_id) for doc_id in posting_list.split('-') if doc_id.strip()]
            matching_docs = self.meta_file_df[self.meta_file_df.index.isin(doc_ids)].to_dict(orient='records')
            return matching_docs
        else:
            return []

    def evaluate_query(self, query):
        """Evaluates the query against the inverted index

        :param query: boolean expression to search for
        :returns: list of dictionaries representing matching documents
        """
        stack = Stack()

        for token in query:
            if token not in ['&', '|', '~']:
                stack.push(self.get_matching_docs(token))  # Push the matching docs directly
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
        all_docs = set(self.meta_file_df.index)
        operand_ids = [doc['ID'] for doc in operand]
        return list(all_docs - set(operand_ids))

