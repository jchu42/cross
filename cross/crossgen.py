import random
import requests
import json
import re
import sys

class CrossGen():
    """Generate a crossword

    Yes, it is incredibly mashed together
    Yes, there's no testing
    Yes, it's super slow and should be its own API thing so ought to pre-generate crosswords so the user doesn't have to wait

    I know
    """
    def __init__(self, size):
        print ("Loading words...")
        self.allwords:list[int, dict[dict[dict[list[str]]]]] = [0, {}]
        self.generate_dicts(size)


    def generate_dicts (self, fixed_length)->None:
        """Read file and generate allwords dict with valid words substrings"""
        self.allwords[0] = fixed_length
        self.allwords[1] = {}
        with open ("cross/words.txt", "r", encoding="UTF") as file:
            for word in file:
                word = word[0:len(word)-1].lower()
                if len(word) > fixed_length*2 or len(word) < fixed_length:
                    continue
                for i in range(len(word)-fixed_length + 1):
                    subdict = self.allwords[1]
                    for j in range(i, i + fixed_length):
                        if word[j] not in subdict:
                            if j == i + fixed_length - 1:
                                subdict[word[j]] = []
                            else:
                                subdict[word[j]] = {}
                        subdict = subdict[word[j]]
                    subdict.append(word)

    def get_words(self, chars)->dict|list[str]:
        """Take sequence of characters, and use allwords dict to find all words that have that substring
        
        Returns
        -------
        list[str]
            list of words with that substring
        """
        if len(chars) > self.allwords[0]:
            raise Exception ("chars length is too long - dicts' length is", self.allwords[0])
        subdict = self.allwords[1]
        for letter in chars:
            if letter not in subdict:
                if len(chars) == self.allwords[0]:
                    return []
                else:
                    return {}
            subdict = subdict[letter]
        return subdict

    def generate_cross(self)->list[list[tuple[str, str]], list[tuple[str, str]]]:
        """Runs the generate cross, starting from an empty state.

        Returns
        list[list[tuple[str, str]], list[tuple[str, str]]]
            The resulting crossword. Each tuple contains the word, 
            and the substring that goes into the dimension x dimension area. 
        """
        attempts = 0
        while True:
            # may run indefinitely, but that's a risk we're willing to take
            res = self.__generate_cross([[], []])
            if res is not None:
                break
            attempts += 1
            print ("Generating failed. trying again...(" + str(attempts) + ")")
        return res
    def __generate_cross(self, curstate:list[list[tuple[str, str]], list[tuple[str, str]]]):
        """Generate a crossword with the dimension x dimension used to create the dictionary.
        
        Parameters
        ----------
        curstate: list[list[tuple[str, str]], list[tuple[str, str]]]
            The current state when it's calling itself. Do not pass a parameter into this function. 

        Returns
        list[list[tuple[str, str]], list[tuple[str, str]]]
            The resulting crossword. Each tuple contains the word, 
            and the substring that goes into the dimension x dimension area. 
        """
        #print ("state: ")
        #print (curstate)
        if len(curstate[1]) < len(curstate[0]):
            prevchars = ""
            for _, subset in curstate[0]:
                prevchars += subset[len(curstate[1])]
            val = self.get_words(prevchars)
            if len(val) == 0:
                return None
            for _ in range(5): # arbitrary number of attempts
                addedchars = ""
                valval = val
                for _ in range (len(prevchars), self.allwords[0]):
                    charchoice, _ = random.sample(sorted(valval.items()), 1)[0]
                    addedchars += charchoice
                    valval = valval[charchoice]
                    if len(valval) == 0:
                        return None
                wordchoice = (random.choice(valval), prevchars + addedchars)
                if wordchoice in curstate[0] or wordchoice in curstate[1]:
                    continue
                res = self.__generate_cross([curstate[0], [*curstate[1], wordchoice]])
                if res is not None:
                    return res
            return None
        elif len(curstate[0]) < self.allwords[0]:
            prevchars = ""
            for _, subset in curstate[1]:
                prevchars += subset[len(curstate[0])]
            val = self.get_words(prevchars)
            if len(val) == 0:
                return None
            for _ in range(5): # arbitrary number of attempts
                addedchars = ""
                valval = val
                for _ in range (len(prevchars), self.allwords[0]):
                    charchoice, _ = random.sample(sorted(valval.items()), 1)[0]
                    addedchars += charchoice
                    valval = valval[charchoice]
                    if len(valval) == 0:
                        return None
                wordchoice = (random.choice(valval), prevchars + addedchars)
                if wordchoice in curstate[0] or wordchoice in curstate[1]:
                    continue
                res = self.__generate_cross([[*curstate[0], wordchoice], curstate[1]])
                if res is not None:
                    return res
            return None
        else:
            return curstate
        
    def to_str_array(self, cross: list[list, list])->tuple[int, int, int, list[str]]:
        """
        space for no character
        """
        to_ret = [""]
        spacingx = max([tup[0].find(tup[1]) for tup in cross[0]])
        spacingy = max([tup[0].find(tup[1]) for tup in cross[1]])
        for i in range(spacingy):
            to_ret[-1] += '_'*spacingx
            for word, substr in cross[1]:
                index = word.find(substr) - spacingy + i
                if index < 0:
                    to_ret[-1] += '_'
                else:
                    to_ret[-1] += word[index]
            to_ret.append("")
        #print()
        for word, substr in cross[0]:
            spaces = spacingx - word.find(substr)
            to_ret[-1] += ('_'*spaces) + word
            to_ret.append("")
        #print()
        i = 0
        while True:
            used = False
            to_ret[-1] += ('_'*spacingx)
            for word, substr in cross[1]:
                index = word.find(substr) + len(substr) + i
                if index < len(word):
                    to_ret[-1] += word[index]
                    used = True
                else:
                    to_ret[-1] += "_"
            if not used:
                break
            i += 1
            to_ret.append("")
        to_ret.pop()
        return (spacingx, spacingy, len(cross[0][0][1]), to_ret)

    OUTPUT_LIMIT = 120
    def get_hint(self, word)->list[str, str]:
        """Generates a hint for the given word
        
        Returns
        -------
        list[
            str
                The type of hint
            str
                The hint
        ]
        """
        try:
            response = requests.get("https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext&titles=" + word)
            if response.status_code != 200:
                return ("uh oh, couldn't find wikipedia link for word '" + word + "'")
            response = json.loads(response.content)
            content = (next(iter(response['query']['pages'].values()))['extract'])[:200]
            # # choose random header
            # if headers_cnt > 1:
            #     headers_cnt = random.randrange(1, headers_cnt)
            # else:
            #     headers_cnt = 0
            # for i, line in enumerate(content):
            #     if headers_cnt == 0:
            #         content = content[i:]
            #         break
            #     if "==" in line:
            #         headers_cnt -= 1
            # for i, line in enumerate(content):
            #     if "==" in line:
            #         content = content[0:i]
            #         break
            # content = content[random.randrange(0, len(content)-1)]

            # thing = re.compile(re.escape(word), re.IGNORECASE)
            # content = thing.sub("_"*len(word), content)
            # content = content[:200] # cap max
            if "==" not in content and "may refer to" not in content and len(content) > 0 and "<!--" not in content:
                # https://stackoverflow.com/questions/14596884/remove-text-between-and
                content = re.sub("[\(\[].*?[\)\]]", '', content)
                if content.find(".") > self.OUTPUT_LIMIT/2:
                    content = content[:content.find(".") + 1]
                content.replace("\n", "")

                thing = re.compile(re.escape(word), re.IGNORECASE)
                content = thing.sub("_"*len(word), content)

                if len(content) > self.OUTPUT_LIMIT:
                    content = content[:self.OUTPUT_LIMIT-3] + "..."
                return ["wikipedia", content]
        except Exception:
            if (next(iter(response['query']['pages'].values()))['missing'] != ""):
                print ("wacc: ", word)


        try:
            #response2 = requests.get("https://www.dictionaryapi.com/api/v3/references/collegiate/json/" + word + "?key=f687a725-b772-4299-a785-8e048c28c532")
            response2 = requests.get("https://www.dictionaryapi.com/api/v3/references/thesaurus/json/" + word + "?key=963fe6bc-9b6c-4b47-976e-74c1583e182e")
            #print(response.content)
            response2 = json.loads(response2.content)
            if isinstance(response2, list):
                response = response2[0]
            else:
                response = response2
            #response = json.loads("""b'[{"meta":{"id":"government","uuid":"e7e3c71d-cafb-48f0-8fb6-7288b19f0767","src":"coll_thes","section":"alpha","target":{"tuuid":"a298af10-6a2f-4654-aca0-27ef93df8fa2","tsrc":"collegiate"},"stems":["government","governmental","governmentalize","governmentalized","governmentalizes","governmentalizing","governmentally","governments"],"syns":[["administration","authority","governance","jurisdiction","regime","regimen","rule"],["administration","care","charge","conduct","control","direction","governance","guidance","handling","intendance","management","operation","oversight","presidency","regulation","running","stewardship","superintendence","superintendency","supervision"]],"ants":[],"offensive":false},"hwi":{"hw":"government"},"fl":"noun","def":[{"sseq":[[["sense",{"sn":"1","dt":[["text","lawful control over the affairs of a political unit (as a nation) "],["vis",[{"t":"{it}government{\\/it} by the people, for the people"}]]],"syn_list":[[{"wd":"administration"},{"wd":"authority"},{"wd":"governance"},{"wd":"jurisdiction"},{"wd":"regime","wvrs":[{"wvl":"also","wva":"r\\u00e9gime"}]},{"wd":"regimen"},{"wd":"rule"}]],"rel_list":[[{"wd":"reign"}],[{"wd":"dominion"},{"wd":"power"},{"wd":"sovereignty","wvrs":[{"wvl":"also","wva":"sovranty"}]},{"wd":"supremacy"},{"wd":"sway"}],[{"wd":"command"},{"wd":"leadership"}],[{"wd":"direction"},{"wd":"management"},{"wd":"regulation"},{"wd":"superintendence"},{"wd":"supervision"}],[{"wd":"autocracy"},{"wd":"dictatorship"},{"wd":"domination"},{"wd":"hegemony"},{"wd":"mastery"},{"wd":"oppression"},{"wd":"subjugation"},{"wd":"tyranny"}]]}]],[["sense",{"sn":"2","dt":[["text","the act or activity of looking after and making decisions about something "],["vis",[{"t":"a board involved in the {it}government{\\/it} of the distribution of benefits to veterans"}]]],"syn_list":[[{"wd":"administration"},{"wd":"care"},{"wd":"charge"},{"wd":"conduct"},{"wd":"control"},{"wd":"direction"},{"wd":"governance"},{"wd":"guidance"},{"wd":"handling"},{"wd":"intendance"},{"wd":"management"},{"wd":"operation"},{"wd":"oversight"},{"wd":"presidency"},{"wd":"regulation"},{"wd":"running"},{"wd":"stewardship"},{"wd":"superintendence"},{"wd":"superintendency"},{"wd":"supervision"}]],"rel_list":[[{"wd":"generalship"},{"wd":"leadership"},{"wd":"rulership"}],[{"wd":"agency"}],[{"wd":"aegis","wvrs":[{"wvl":"also","wva":"egis"}]},{"wd":"custody"},{"wd":"guardianship"},{"wd":"keeping"},{"wd":"lap"},{"wd":"protection"},{"wd":"safekeeping"},{"wd":"trust"},{"wd":"tutelage"},{"wd":"ward"}],[{"wd":"engineering"},{"wd":"logistics"},{"wd":"machination"},{"wd":"manipulation"}],[{"wd":"coadministration"},{"wd":"codirection"},{"wd":"comanagement"}]]}]]]}],"shortdef":["lawful control over the affairs of a political unit (as a nation)","the act or activity of looking after and making decisions about something"]},{"meta":{"id":"government","uuid":"5b15eea7-09ea-4d73-887c-8f02dd0cb0bd","src":"CTcompile","section":"alpha","stems":["government"],"syns":[["governmental","civic","federal","municipal","domestic","internal","intestine","civil","national","public","democratic","republican","nationwide"]],"ants":[["nonnational","global","international","alien","external","foreign"]],"offensive":false},"hwi":{"hw":"government"},"fl":"adjective","def":[{"sseq":[[["sense",{"dt":[["text","as in {it}governmental{\\/it}"]],"sim_list":[[{"wd":"governmental"}],[{"wd":"civic"},{"wd":"federal"},{"wd":"municipal"}],[{"wd":"domestic"},{"wd":"internal"},{"wd":"intestine"}],[{"wd":"civil"},{"wd":"national"},{"wd":"public"}],[{"wd":"democratic"},{"wd":"republican"}],[{"wd":"nationwide"}]],"opp_list":[[{"wd":"nonnational"}],[{"wd":"global"},{"wd":"international"}],[{"wd":"alien"},{"wd":"external"},{"wd":"foreign"}]]}]]]}],"shortdef":["as in governmental"]},{"meta":{"id":"self-government","uuid":"01eee1b7-1fb2-4a08-9cbd-4a8c7ef8aa9f","src":"coll_thes","section":"alpha","target":{"tuuid":"f358a068-5383-495a-8e0a-3e9d9fc30220","tsrc":"collegiate"},"stems":["self-government","self-governments"],"syns":[["democracy","republic","self-rule"],["continence","restraint","self-command","self-containment","self-control","self-discipline","self-mastery","self-possession","self-restraint","will","willpower"],["autonomy","freedom","independence","independency","liberty","self-determination","self-governance","sovereignty"]],"ants":[["dependence","heteronomy","subjection","unfreedom"]],"offensive":false},"hwi":{"hw":"self-government"},"fl":"noun","def":[{"sseq":[[["sense",{"sn":"1","dt":[["text","government in which the supreme power is held by the people and used by them directly or indirectly through representation "],["vis",[{"t":"{it}self-government{\\/it} implies faith in the wisdom and essential goodness of the people"}]]],"syn_list":[[{"wd":"democracy"},{"wd":"republic"},{"wd":"self-rule"}]],"rel_list":[[{"wd":"pure democracy"}],[{"wd":"home rule"},{"wd":"self-determination"}],[{"wd":"autonomy"},{"wd":"sovereignty","wvrs":[{"wvl":"also","wva":"sovranty"}]}]],"near_list":[[{"wd":"despotism"},{"wd":"dictatorship"},{"wd":"monarchy"},{"wd":"monocracy"},{"wd":"totalitarianism"},{"wd":"tyranny"}]]}]],[["sense",{"sn":"2","dt":[["text","the power to control one\\u0027s actions, impulses, or emotions "],["vis",[{"t":"steely {it}self-government{\\/it} was all that kept her from lashing out at the rude customer"}]]],"syn_list":[[{"wd":"continence"},{"wd":"restraint"},{"wd":"self-command"},{"wd":"self-containment"},{"wd":"self-control"},{"wd":"self-discipline"},{"wd":"self-mastery"},{"wd":"self-possession"},{"wd":"self-restraint"},{"wd":"will"},{"wd":"willpower"}]],"rel_list":[[{"wd":"self-abnegation"},{"wd":"self-denial"}],[{"wd":"moderateness"},{"wd":"moderation"},{"wd":"temperance"},{"wd":"temperateness"}],[{"wd":"determination"},{"wd":"nerve"}],[{"wd":"command"},{"wd":"control"},{"wd":"discipline"},{"wd":"mastery"}],[{"wd":"abnegation"},{"wd":"abstention"},{"wd":"avoidance"},{"wd":"eschewal"},{"wd":"forbearance"}],[{"wd":"abstinence"},{"wd":"soberness"},{"wd":"sobriety"}],[{"wd":"aplomb"},{"wd":"assurance"},{"wd":"composure"},{"wd":"confidence"},{"wd":"coolness"},{"wd":"equanimity"},{"wd":"poise"},{"wd":"self-confidence"}],[{"wd":"discretion"}]],"near_list":[[{"wd":"gratification"},{"wd":"indulgence"},{"wd":"self-indulgence"}],[{"wd":"excessiveness"},{"wd":"immoderacy"},{"wd":"intemperance"},{"wd":"intemperateness"},{"wd":"overindulgence"}],[{"wd":"demerit"},{"wd":"failing"},{"wd":"fault"},{"wd":"feebleness"},{"wd":"foible"},{"wd":"frailty"},{"wd":"shortcoming"},{"wd":"vice"},{"wd":"weakness"}],[{"wd":"indiscipline"},{"wd":"unconstraint"},{"wd":"unreserve"},{"wd":"unreservedness"},{"wd":"unrestraint"}]]}]],[["sense",{"sn":"3","dt":[["text","the state of being free from the control or power of another "],["vis",[{"t":"championed {it}self-government{\\/it} for the nation\\u0027s indigenous peoples"}]]],"syn_list":[[{"wd":"autonomy"},{"wd":"freedom"},{"wd":"independence"},{"wd":"independency"},{"wd":"liberty"},{"wd":"self-determination"},{"wd":"self-governance"},{"wd":"sovereignty","wvrs":[{"wvl":"also","wva":"sovranty"}]}]],"rel_list":[[{"wd":"emancipation"},{"wd":"enfranchisement"},{"wd":"liberation"},{"wd":"manumission"},{"wd":"release"}]],"near_list":[[{"wd":"captivity"},{"wd":"enchainment"},{"wd":"enslavement"},{"wd":"immurement"},{"wd":"imprisonment"},{"wd":"incarceration"},{"wd":"internment"},{"wd":"subjugation"}]],"ant_list":[[{"wd":"dependence","wvrs":[{"wvl":"also","wva":"dependance"}]},{"wd":"heteronomy"},{"wd":"subjection"},{"wd":"unfreedom"}]]}]]]}],"shortdef":["government in which the supreme power is held by the people and used by them directly or indirectly through representation","the power to control one\\u0027s actions, impulses, or emotions","the state of being free from the control or power of another"]}]'""")
            if 'meta' not in response or response['meta']['id'].split(":")[0] != word:
                # use other api, because fuggit
                response2 = requests.get("https://www.dictionaryapi.com/api/v3/references/collegiate/json/" + word + "?key=f687a725-b772-4299-a785-8e048c28c532")
                response2 = json.loads(response2.content)
                if isinstance(response2, list):
                    response = response2[0]
                else:
                    response = response2
            response = response['def']
            response = response[random.randrange(len(response))]
            response = response['sseq']
            response = response[random.randrange(len(response))]
            response = response[random.randrange(len(response))]#uhh
            response = response[1]
            choices = []
            try:
                # https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists
                choices.append(["synonyms", "; ".join([element["wd"] for vals in response['syn_list'] for element in vals])])
            except Exception as e:
                pass
            try:
                choices.append(["related", "; ".join([element["wd"] for vals in response['rel_list'] for element in vals])])
            except Exception as e:
                pass
            try:
                choices.append(["similar", "; ".join([element["wd"] for vals in response['sim_list'] for element in vals])])
            except Exception as e:
                pass
            try:
                choices.append(["opposite", "; ".join([element["wd"] for vals in response['opp_list'] for element in vals])])
            except Exception as e:
                pass
            if len(choices) == 0:
                try:
                    choices.append(["definition", response['dt'][0][1]])
                except Exception as e:
                    pass
                try:
                    choices.append(["example", response['dt'][1][1][0]['t']])
                except Exception as e:
                    pass
            ret = random.choice(choices)
            
            # https://stackoverflow.com/questions/919056/case-insensitive-replace
            thing = re.compile(re.escape(word), re.IGNORECASE)
            ret[1].replace('{', "|")
            ret[1].replace('}', "|") # bogus shenanigans, because "{it}" and {"/it"} are weird because curly brackets
            ret[1].replace('|it|', "")
            ret[1].replace('|/it|', "")
            ret[1] = thing.sub("_"*len(word), ret[1])
            if len(ret[1]) > self.OUTPUT_LIMIT:
                ret[1] = ret[1][:self.OUTPUT_LIMIT-3]+"..." # limit output
            return ret
        except Exception:
            if 'ret' in locals():
                print ("return was: ")
                print (ret)
            print ("response for " + word + ":")
            print (response2)
            raise Exception
        # have had to remove:
        # - athlete

    def generate_puzzle(self)->tuple[int, int, int, list[str], list[str], list[str]]:
        """Generate a puzzle and create hints

        Returns
        -------
        tuple[
            int
                number of letters until start of common letters (x)
            int
                number of letters until start of common letters (y)
            int
                number of common letters
            list[str]
                letters, where space is no letter, and letter is a letter
            list[str]
                'across' hints
            list[str]
                'down' hints
        ]
        """
        res = self.generate_cross()
        spacingx, spacingy, length, arr = self.to_str_array(res)
        while len(arr) < 12:
            arr.append("")
        for x, line in enumerate(arr):
            while len(arr[x]) < 12:
                arr[x] += "_"

        # for y, line in enumerate(arr):
        #     for x, char in enumerate(line):
        #         if x >= spacingx and x < spacingx + length and y >= spacingy and y < spacingy + length:
        #             print (char.upper(), end='')                
        #         else:
        #             print (char, end='')
        #     print()

        # print ("Hints")
        # print ("-----")
        # print ("Across")

        hintsacross:list[str] = []
        hintsdown:list[str] = []

        for i, (word, _) in enumerate(res[0]):
            hintsacross.append(self.get_hint(word))
            # print (str(i + 1) + ": ", end='')
            # print(self.get_hint(word))
        # print ("Down")
        for i, (word, _) in enumerate(res[1]):
            hintsdown.append(self.get_hint(word))
            # print (str(i + 1) + ": ", end='')
            # print(self.get_hint(word))
        # for y, line in enumerate(arr):
        #     for x, char in enumerate(line):
        #         if x >= spacingx and x < spacingx + length and y >= spacingy and y < spacingy + length:
        #             print ("-", end='')
        #         elif char == " ":
        #             print (" ", end='')
        #         else:
        #             print ("_", end='')
        #     print()
        return(spacingx, spacingy, length, arr, hintsacross, hintsdown)