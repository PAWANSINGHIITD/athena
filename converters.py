import math
from typing import Tuple

class NumeralSystem:
    def to_culture(self, number:int)->str:
        raise NotImplementedError
    def to_arabic(self, text:str)->int:
        raise NotImplementedError
    def explain_to_culture(self, number:int)->str:
        return ""
    def explain_to_arabic(self, text:str)->str:
        return ""

# --- Roman system ---
class RomanSystem(NumeralSystem):
    roman_map = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]
    def to_culture(self, number:int)->str:
        n=number
        result=""
        for value, symbol in self.roman_map:
            while n>=value:
                result+=symbol
                n-=value
        return result
    def to_arabic(self, text:str)->int:
        s=text.upper()
        values={sym:val for val,sym in [(v,k) for (v,k) in [(v,k) for v,k in self.roman_map]]}
        # simpler approach
        mapping = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}
        total=0; i=0
        while i<len(s):
            if i+1<len(s) and mapping[s[i]]<mapping[s[i+1]]:
                total += mapping[s[i+1]]-mapping[s[i]]
                i+=2
            else:
                total += mapping[s[i]]
                i+=1
        return total
    def explain_to_culture(self, number:int)->str:
        steps=[]; n=number
        for value,symbol in self.roman_map:
            count = n//value
            if count:
                steps.append(f"{value} fits {count} time(s): add '{symbol'*count}'")
                n = n%value
        if not steps:
            steps.append("Zero or unsupported")
        return " ; ".join(steps)
    def explain_to_arabic(self, text:str)->str:
        return f"Parsed Roman numeral '{text}' by scanning symbols and applying subtractive rules."

# --- Babylonian (base 60) simplified rendering ---
class BabylonianSystem(NumeralSystem):
    def to_culture(self, number:int)->str:
        # break into base-60 places; represent as comma-separated place values
        if number==0: return "𒐕"  # zero placeholder (not historically exact)
        parts=[]
        n=number
        while n>0:
            parts.append(str(n%60))
            n//=60
        return "[" + "][".join(reversed(parts)) + "] (places base-60)"
    def to_arabic(self, text:str)->int:
        # expects format like [a][b][c]
        clean = text.replace("]","[").strip("[]")
        if not clean: return 0
        parts = [p for p in clean.split("[") if p]
        total=0
        for p in parts:
            total = total*60 + int(p)
        return total
    def explain_to_culture(self, number:int)->str:
        parts=[]
        n=number
        place=0
        while n>0:
            parts.append(f"place {place}: {n%60}")
            n//=60; place+=1
        parts.reverse()
        return " ; ".join(parts)

# --- Mayan (dot-bar) simplified ---
class MayanSystem(NumeralSystem):
    def to_culture(self, number:int)->str:
        # use base-20 with special 3rd place (simplified)
        if number==0: return "○ (shell for zero)"
        parts=[]
        n=number
        while n>0:
            parts.append(n%20)
            n//=20
        # represent each place as dots/bars
        def glyph(v):
            bars = v//5
            dots = v%5
            return "-"*bars + "."*dots if v else "○"
        return " | ".join(reversed([glyph(p) for p in parts]))
    def to_arabic(self, text:str)->int:
        # parse '|' separated glyphs with '-' as bars and '.' as dots
        parts = [p.strip() for p in text.split("|")]
        total=0
        for p in parts:
            if p=="○": v=0
            else:
                v = p.count("-")*5 + p.count(".")
            total = total*20 + v
        return total
    def explain_to_culture(self, number:int)->str:
        return "Converted to base-20 places and rendered each place with bars (5) and dots (1)."

# --- Chinese numerals (simplified mapping up to 9999) ---
class ChineseSystem(NumeralSystem):
    digits = {0:"零",1:"一",2:"二",3:"三",4:"四",5:"五",6:"六",7:"七",8:"八",9:"九"}
    units = [(1000,"千"),(100,"百"),(10,"十")]
    def to_culture(self, number:int)->str:
        if number==0: return "零"
        parts=[]
        n=number
        if n>=1000:
            q=n//1000; parts.append(self.digits[q]+"千"); n%=1000
        if n>=100:
            q=n//100; parts.append(self.digits[q]+"百"); n%=100
        if n>=10:
            q=n//10
            if q>1:
                parts.append(self.digits[q]+"十")
            else:
                parts.append("十")
            n%=10
        if n>0:
            parts.append(self.digits[n])
        return "".join(parts)
    def to_arabic(self, text:str)->int:
        # simple reverse for numbers <10000
        txt = text.replace("零","0")
        # naive mapping
        num = 0; tmp=""
        unit_map = {"千":1000,"百":100,"十":10}
        val_map = {v:k for k,v in self.digits.items()}
        i=0; cur=0
        while i<len(text):
            ch=text[i]
            if ch in val_map:
                cur = val_map[ch]
                i+=1
                if i<len(text) and text[i] in unit_map:
                    num += cur*unit_map[text[i]]
                    cur=0; i+=1
                else:
                    num += cur; cur=0
            elif ch in unit_map:
                num += unit_map[ch]; i+=1
            else:
                i+=1
        return num
    def explain_to_culture(self, number:int)->str:
        return "Decomposed number into thousands, hundreds, tens and ones and used Chinese characters."

# --- Yoruba simplified ---
class YorubaSystem(NumeralSystem):
    base_words = {1:"okan",2:"eeji",3:"eeta",4:"eerin",5:"aarun",10:"mewa",20:"ogun"}
    def to_culture(self, number:int)->str:
        if number in self.base_words:
            return self.base_words[number]
        if number<20:
            return f"{number} (Yoruba irregular form)"
        # for demonstration we use straightforward compound
        tens = (number//20)*20
        rest = number%20
        if rest==0:
            return self.base_words.get(tens,str(tens))
        return f"{self.base_words.get(tens,str(tens))} + {self.to_culture(rest)}"
    def to_arabic(self, text:str)->int:
        reverse = {v:k for k,v in self.base_words.items()}
        if text in reverse: return reverse[text]
        if "+" in text:
            parts = [p.strip() for p in text.split("+")]
            s=0
            for p in parts:
                s += self.to_arabic(p) if not p.isdigit() else int(p)
            return s
        try:
            return int(text)
        except:
            return -1
    def explain_to_culture(self, number:int)->str:
        return "Yoruba historically uses vigesimal (base-20) compounds; we approximate compounds here."

# --- Inuktitut placeholder (uses Arabic digits but shows cultural notes) ---
class InuktitutSystem(NumeralSystem):
    def to_culture(self, number:int)->str:
        return str(number) + " (Inuktitut numeric convention: modern practice often uses Arabic digits; local scripts vary)"
    def to_arabic(self, text:str)->int:
        try:
            return int(text.split()[0])
        except:
            return -1
    def explain_to_culture(self, number:int)->str:
        return "Inuktitut historically had counting practices tied to body-part tallies; modern use commonly uses Arabic digits."

# Registry and converter facade
class NumeralConverter:
    def __init__(self):
        self.systems = {
            "roman": RomanSystem(),
            "babylonian": BabylonianSystem(),
            "mayan": MayanSystem(),
            "chinese": ChineseSystem(),
            "yoruba": YorubaSystem(),
            "inuktitut": InuktitutSystem()
        }
    def convert_with_explanation(self, number:int, system_key:str)->tuple:
        sys = self.systems.get(system_key)
        if not sys: raise ValueError("Unknown system")
        return sys.to_culture(number), sys.explain_to_culture(number)
    def parse_with_explanation(self, text:str, system_key:str)->tuple:
        sys = self.systems.get(system_key)
        if not sys: raise ValueError("Unknown system")
        return sys.to_arabic(text), sys.explain_to_arabic(text)
