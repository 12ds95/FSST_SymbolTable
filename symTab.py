import heapq
MAX_SYM_LENGTH = 8

class StrCmp:
  def __init__(self, val):
      self.val = val

  def __lt__(self, other):
      min_len = min((len(self.val), len(other.val)))
      if self.val[:min_len] == other.val[:min_len]:
          return len(self.val) > len(other.val)
      else:
          return self.val < other.val

class SymbolTable:
  # constructor
  def __init__(self): 
    self.nSymbols = 0
    self.sIndex = [0]*257 # len = 257, to avoid testing if letter+1 is out-of-range in findLongestSymbol
    self.symbols = ['']*512 # the firself 256 symbols are escaped bytes 
    for code in range(0,256):
      self.symbols[code] = chr(code) 

  def insert(self, s):
    self.symbols[256+self.nSymbols] = s
    self.nSymbols += 1

  def findLongestSymbol(self, text):
    letter = ord(text[0])
    # try all symbols that start with this letter
    for code in range(self.sIndex[letter],self.sIndex[letter+1]):
      if text.find(self.symbols[code]) != -1: 
        return code # symbol, code >= 256
    return letter # non-symbol byte (will be escaped)

  # compress the sample and count the frequencies
  def compressCount(self, count1, count2, text):
    pos = 0
    prev = None
    while True:
      code = self.findLongestSymbol(text[pos:])
      # count the frequencies
      count1[code] += 1
      if prev != None:
        count2[prev][code] += 1
        s = (self.symbols[prev]+ self.symbols[code])[:MAX_SYM_LENGTH] 
      # we also count frequencies for the next byte only
      if code >= 256 and prev != None:
        nextByte = ord(text[pos]) 
        count1[nextByte] += 1
        count2[prev][nextByte] += 1
        s = (self.symbols[prev]+ self.symbols[nextByte])[:MAX_SYM_LENGTH] 
      prev = code
      pos += len(self.symbols[code])
      if pos == len(text):
        break

  # pick top symbols 
  def makeTable(self, count1, count2): 
    cands = {}
    heap = []
    for code1 in range(0,256+self.nSymbols):
      # single symbols (+all bytes 0..255) are candidates
      gain = len(self.symbols[code1]) * count1[code1]
      cands[self.symbols[code1]] = 1 if code1 < 256 and gain == 0 else gain # single charater gains at least 1
      for code2 in range(0,256+self.nSymbols):
        # concatenated symbols are also candidates
        s = (self.symbols[code1] + self.symbols[code2])[:MAX_SYM_LENGTH] 
        gain = len(s) * count2[code1][code2]
        cands[s] = cands.get(s, 0) + gain
    for cand in cands.items():
      heap.append((-cand[1], cand[0]))
    heapq.heapify(heap)
    # fill with the most worthwhile candidates
    self.nSymbols = 0
    while self.nSymbols < 255:
      v = heapq.heappop(heap)
      self.insert(v[1])
    return self.makeIndex()

  # make index for findLongestSymbol
  def makeIndex(self): 
    # sort the real symbols and init the letter index
    self.sIndex = [0]*257
    tmp = sorted(self.symbols[256:256+self.nSymbols], key=StrCmp)
    for i in reversed(range(self.nSymbols)):
      letter = ord(tmp[i][0]) 
      self.sIndex[letter] = 256+i # latter has higher opportunity
      self.symbols[256+i] = tmp[i]
      if self.sIndex[letter+1] == 0: # (self.sIndex[letter], self.sIndex[letter+1]-1) stands for symbols begin with the same letter
        self.sIndex[letter+1] = 256+i+1
    self.sIndex[256] = 256+self.nSymbols # sentinel 
    return self

  def buildSymbolTable(self, text): # top-level entry point 
    for _ in range(5):
      count1 = [0]*512
      count2 = [[0]*512 for i in range(512)]
      self.compressCount(count1, count2, text) 
      self.makeTable(count1, count2)
    return self

if __name__ == "__main__":
    # run test case in paper section 4.2
    MAX_SYM_LENGTH = 3
    text = "tumcwitumvldb"
    res = SymbolTable()
    res.buildSymbolTable(text)
    print(res.symbols[256:])
    
    pos = 0
    prev = None
    encoded_text = "|"
    while True:
      code = res.findLongestSymbol(text[pos:])
      # count the frequencies
      if prev != None:
        s = (res.symbols[prev]+ res.symbols[code])[:MAX_SYM_LENGTH] 
        print("prev={}: code={}, candidate_concat_str={}".format(res.symbols[prev], res.symbols[code], s))
      else:
        print("prev=None: code={}".format(res.symbols[code]))
      if code >= 256 and prev != None:
        nextByte = ord(text[pos]) 
        s = (res.symbols[prev]+ res.symbols[nextByte])[:MAX_SYM_LENGTH] 
        print("Additionl byte and candidate_concat_str: prev={}, nextByte={}, concat_str={}".format(res.symbols[prev], res.symbols[nextByte], s))
      prev = code
      pos += len(res.symbols[code])
      encoded_text = encoded_text + res.symbols[code] + '|'
      if pos == len(text):
        break
    print("encoded text: {}".format(encoded_text))