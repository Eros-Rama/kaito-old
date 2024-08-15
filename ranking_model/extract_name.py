import re
import spacy

class extract_name:
    

    def parse_query1(self, query):
        # Regular expression to capture the speaker's name after "SPEAKER_"
        match = re.search(r'SPEAKER_(\w+)', query)
        if match:
            return match.group(1)
        return None
    
    def parse_query2(self, query):
        nlp = spacy.load("en_core_web_lg")
        doc = nlp(query)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return None

    def name_filter(self, query):
        
        
        speaker_name = self.parse_query1(query)
        if speaker_name == None :
            speaker_tag = self.parse_query2(query)
            print(speaker_tag)  # Output: 'Rocky John'
            return speaker_tag
        else : 
            print("SPEAKER_" + speaker_name)  # Output: '39'
            speaker_name = "SPEAKER_" + speaker_name
            return speaker_name 


# if __name__ == "__main__":
#     en = extract_name()
#     query = "What does Ameen Soleimani think about the influence of in global practices?"
#     en.name_filter(query)