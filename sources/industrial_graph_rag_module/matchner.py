import os
from pathlib import Path
from typing import Dict, TypeAlias, Union
import traceback
import json
from warnings import warn
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.llms.base import BaseLLM
from langchain.chains import LLMChain
from langchain_core.language_models import BaseLanguageModel

FilePathType: TypeAlias = Union[str, bytes, os.PathLike]

# used only for LLMMatchner
NER_PROMPT_TEMPLATE = """
Task:   Identify and match the named entities from a given text and given list. a word or phrase must be associated with a single entity in the list if there is a match, but not every word or phrase have to have a corresponding item in the list. Find exact matches or semantic matches or syntactic similar matches. 
given text:
{prompt}
given list:
{entity_list}
Output the result as a JSON array of dictionaries, each with keys "matched_text" and "entity".
Example of the output format: [{{"matched_text": "text from prompt", "entity": "entity from list"}}, ...]
"""
#Please dont return any sting like ```json ... ```. Just return the json object as string

def entity_mapping_loader(mapping_path: str) -> pd.DataFrame:
    assert mapping_path.endswith(".csv"), "entity mapping file must be a .csv file"
    return pd.read_csv(mapping_path, sep=",")


# refactored this function's return statement
def get_llm_ner_chain(prompt_template: str, llm: BaseLLM) -> LLMChain:
    ner_prompt = PromptTemplate(
        input_variables=["prompt", "entity_list"],
        template=prompt_template,
    )
    return LLMChain(llm=llm, prompt=ner_prompt)

def llm_matcher(kw_list: str, query: str, ner_chain: LLMChain):
    matched_output = ner_chain.predict(
        prompt=query,
        entity_list=kw_list,
    )
    
    try:
        start = '```json'
        end = '```'
        tt0 = matched_output.find(start)
        tt = tt0 + len(start)
        s2 = matched_output[tt:]
        zz = s2.find(end)
        json_output = s2[:zz]
        if tt0 == -1 or zz == -1:
            return json.loads("{}")
        parsed_match = json.loads(json_output)
        print("DEBUG parsed match: ", parsed_match)
        
        # extra validation to catch unexpected outputs like empty outputs
        
        if isinstance(parsed_match, list) and all(
            isinstance(item, dict) and 'matched_text' in item and 'entity' in item for item in parsed_match
        ):
            match = {item['matched_text']: item['entity'] for item in parsed_match}
            
        else:
            raise ValueError("Invalid output format from LLM.")
            
    except Exception:
        match = {} # when there is an exception in the format of the match, print the exception and return empty match
        # maybe we want to change this
        
        print("Error!")
        print(f"LLM output:{matched_output}")
        print(traceback.format_exc())
        
    return match

# did not touch this
class BaseMatchner:
    # todo: refactor the mapping list and matching logic in different modules.-> matching_engine, mapping_engine
    def __init__(self, **kwargs):
        self.entity_mapping = None  # todo: improve it later by refactoring
        # todo: do a better approach probably with iterator / generator

    # @abstractmethod
    def match(self, query: str) -> Dict[str, str]:
        raise NotImplementedError("match method must be overridden in child class")

class LLMMatchner(BaseMatchner):  # does NER using LLM to match named entities against a list
    def __init__(
            self,
            entity_mapping_path: str,
            llm: BaseLLM,
            *,
            return_uri: bool = True,
            ner_prompt_template: str = NER_PROMPT_TEMPLATE,
            **kwargs
    ):
        super().__init__()
        self.entity_mapping = entity_mapping_loader(entity_mapping_path)
        self.return_uri = return_uri
        
        # here convert the entity list to a JSON array to handle special characters before feeding it to llm
        
        self.entity_list = json.dumps(self.entity_mapping["label"].values.tolist())
        self._ner_chain = get_llm_ner_chain(ner_prompt_template, llm)  # todo: refactor later
        
        self._json_path = kwargs.get("jsonpath", None)  # experimental, will be removed

        # save the mappings for efficient lookup, instead of sending dataframe queries all the time.
        self.label_to_nodeid = self.entity_mapping.set_index('label')['nodeid'].to_dict()
        self.label_to_subject_uri = self.entity_mapping.set_index('label')['subject_uri'].to_dict()

    def match(self, query: str) -> tuple[Dict[str, str], Dict[str, str]]:
    
        # we remove the quotation marks from the query but I think this is no longer necessary
        query = query.replace('"', '').replace("'", "")
        match = llm_matcher(self.entity_list, query, self._ner_chain)
        
        original_match = match.copy()  # we need this clean copy for match2
        
        if self.return_uri and match:

            # we now use a new dictionary to avoid modifying while iterating
            updated_match = {}
            for k, v in match.items():
                uri = self.get_node_uri(v)
                updated_match[k] = uri
            match = updated_match
        self.json_dump(match)

        match2 = {}
        for k, v in original_match.items():
            subject_uri = self.get_subject_uri(v)
            match2[k] = subject_uri

        print("MATCH ", match, " ", match2)
        return match, match2

    def get_node_uri(self, label: str) -> str:
        return self.label_to_nodeid.get(label, "")

    def get_subject_uri(self, label: str) -> str:
        return self.label_to_subject_uri.get(label, "")

    def json_dump(self, match):
        if not self._json_path:
            return
        else:
            warn(
                "This is an experimental debugging feature."
                "Will be removed in future versions."
                "Please convert the match dict to json yourself instead.",
                DeprecationWarning,
                stacklevel=2
            )
            if isinstance(self._json_path, str) and not self._json_path.endswith(".json"):
                Path(self._json_path).mkdir(exist_ok=True, parents=True)
                json_path = os.path.join(self._json_path, "match.json")
            elif isinstance(self._json_path, FilePathType):
                json_path = self._json_path
            else:
                raise ValueError(f"'jsonpath' must be a string or pathlike object."
                                 f"But obtained {type(self._json_path)} instead.")
            with open(json_path, "w") as json_file:
                json.dump(match, json_file, indent=4)




class LLMListMatchner(BaseMatchner):
    def __init__(
            self,
            llm: BaseLanguageModel,
            kw_list: str = None,  # should be ", " separated sting Ex: "ActualPosition, Robot, Axis"
            ner_prompt_template: str = NER_PROMPT_TEMPLATE,
    ):
        super().__init__()
        self._ner_chain = get_llm_ner_chain(ner_prompt_template, llm)
        self.entity_list = kw_list

    def match(
            self,
            query: str,
            dyn_list: str = None  # should be ", " separated sting Ex: "ActualPosition, Robot, Axis"
    ) -> Dict[str, str]:
        if dyn_list:
            match = llm_matcher(dyn_list, query, self._ner_chain)
        elif self.entity_list:
            match = llm_matcher(self.entity_list, query, self._ner_chain)
        else:
            raise ValueError("'entity_list' and 'dyn_list' both can't be None simultaneously")
        return match




class KeywordMatchner(BaseMatchner):  # looks for exact keyword match
    def __init__(self, entity_mapping_path: str, **kwargs):
        super().__init__()
        self.entity_mapping = entity_mapping_loader(entity_mapping_path)

    def match(self, query: str) -> Dict[str, str]:
        match = dict()
        nl_query_words = query.replace("?", "").split(" ")
        for w in nl_query_words:
            if w in self.entity_mapping["label"].values:
                match[w] = self.entity_mapping[self.entity_mapping["label"] == w]["nodeid"].values[0]  # nodeId (label colum must be unique)
        return match