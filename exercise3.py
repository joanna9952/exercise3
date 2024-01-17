import requests
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
nltk.download('punkt')


x = requests.get('https://poetrydb.org/author,title/Shakespeare;Sonnet')
#print(x.text)

json_string = x.text
sonnet_data_dictionary = json.loads(json_string)
#print(sonnet_data_dictionary)


class Document:
    def __init__(self, lines):
        self.lines = lines

    def tokenize(self) -> list[str]:
        porter_stemmer = PorterStemmer()
        all_tokens = []
        for line in self.lines:
            tokens = word_tokenize(line.lower())

            for token in tokens:
                if token not in ['.', ',', "'", ':', ';', '!', '?']:
                    all_tokens.append(porter_stemmer.stem(token))

        return all_tokens


class Sonnet(Document):
    def __init__(self, sonnet_data):

        # Extracting sonnet number from the title
        title_parts = sonnet_data['title'].split(':')  # Splits it into two parts
        title = str(title_parts[1].strip())  # Extracts the title
        sonnet_id = int(title_parts[0].split()[-1].strip())  # Extracts and converts to int
        lines = sonnet_data['lines']
        super().__init__(lines)
        self.id = sonnet_id
        self.title = title

    def __str__(self):
        return f"Sonnet {self.id}: {self.title} \n {'\n'.join(self.lines)}"

    def __repr__(self):
        return self.__str__()


sonnet_instances = []
for current_sonnet in sonnet_data_dictionary:
    sonnet_instance = Sonnet(current_sonnet)
    sonnet_instances.append(sonnet_instance)

#for sonnet_instance in sonnet_instances:
#    print(sonnet_instance)  # Prints all sonnets


class Query(Document):
    def __init__(self, query: str):
        super().__init__([query])


class Index(dict[str, set[int]]):
    def __init__(self, documents: list[Sonnet]):
        super().__init__()

        self.documents = documents

        for document in documents:
            self.add(document)

    def add(self, document: Sonnet):
        tokens = document.tokenize()

        for token in tokens:
            if token not in self:
                self[token] = set()

            self[token].add(document.id)

    def search(self, query: Query) -> list[Sonnet]:
        query_tokens = query.tokenize()

        matching_document_ids = None
        for token in query_tokens:
            if token in self:
                if matching_document_ids is None:
                    matching_document_ids = self[token].copy()
                else:
                    matching_document_ids.intersection_update(self[token])

        matching_sonnets = []
        if matching_document_ids is not None:
            for document_id in matching_document_ids:
                matching_sonnets.append(self.documents[document_id - 1])

        return matching_sonnets


'''
# Build the index
index = Index(sonnet_instances)
query = Query("love hate")  # Build the query
matching_sonnets_from_query = index.search(query)  # Search the index with the query
# Print the results
for matching_sonnet in matching_sonnets_from_query:
    print(matching_sonnet)
    
'''


def user_interface():
    
    index = Index(sonnet_instances)

    print("Reading sonnets...")

    while True:
        search_input = input("Search for sonnets ('q' to quit)> ")
        if search_input.lower() == 'q':
            break

        query = Query(search_input)
        matching_sonnets = index.search(query)

        print(f"--> Your search for '{search_input}' matched {len(matching_sonnets)} sonnets ({', '.join(str(sonnet.id) for sonnet in matching_sonnets)}):")
        for matching_sonnet in matching_sonnets:
            print(matching_sonnet)


user_interface()
