import time

def isdigit(c):
    return c>='0' and c<='9'
def isalpha(c):
    return (c>='a' and c<='z') or (c>='A' and c<='Z')
def isalnum(c):
    return (c>='a' and c<='z') or (c>='A' and c<='Z') or (c>='0' and c<='9')
def ishex(c):
    return isdigit(c) or (c>='a' and c<='f') or (c>='A' and c<='F')

def tokenize(text):
    tokens=[]
    look=text[0]
    lookIndex=0

    def getChar():
        nonlocal look, lookIndex
        lookIndex+=1
        try:
            look=text[lookIndex]
        except:
            look=''

    def peek():
        nonlocal lookIndex
        peekIndex = lookIndex + 1
        if peekIndex>=len(text):
            return ''
        return text[peekIndex]

    def skipWhite():
        nonlocal look
        while look.isspace():
            getChar()


    while look:
        skipWhite()
        
        if not look:
            break

        if isalpha(look):#identifiers
            startIndex=lookIndex
            while isalnum(look):
                getChar()
                if not isalnum(look):                    
                    tokens.append({'t':'n', 'v': text[startIndex:lookIndex]})

        elif look=='0' and peek().lower()=='x':#hex int
            getChar()
            getChar()
            startIndex=lookIndex
            if not ishex(look):
                raise ValueError('bad hex literal')
            while ishex(look):
                getChar()
                
            tokens.append({'t':'i', 'v': int(text[startIndex:lookIndex], 16)})

        elif look=='-' or look=='+' or look=='.' or isdigit(look):#ints, floats, or + - .
            unary=''
            if look=='-' or look=='+':
                unary=look
                getChar()
                skipWhite()
            if not look or not (look=='.' or isdigit(look)):
                tokens.append({'t':'s', 'v': unary})
            else:
                startIndex=lookIndex
                hasDec=False
                notDone=True
                while look and notDone:
                    notDone=False
                    if isdigit(look):
                        notDone=True
                    elif look=='.' and not hasDec:
                        hasDec=True
                        notDone=True
                    if notDone:
                        getChar()
                if lookIndex-startIndex==1 and text[startIndex]=='.':
                    if unary:
                        tokens.append({'t':'s', 'v': unary})
                    tokens.append({'t':'s', 'v': '.'})
                else:
                    if hasDec:
                        val=float(text[startIndex:lookIndex])
                        if unary=='-':
                            val=-val
                        tokens.append({'t':'f', 'v': val})
                    else:
                        val=int(text[startIndex:lookIndex])
                        if unary=='-':
                            val=-val
                        tokens.append({'t':'i', 'v': val})
            
        elif look=='"' or look=="'":#strings
            toMatch = look
            getChar()
            startIndex=lookIndex
            while look and look!=toMatch:
                getChar()
            if look!=toMatch:
                raise ValueError('bad string literal')
            else:
                tokens.append({'t':'$', 'v': text[startIndex:lookIndex]})
                getChar()

        else:#symbols
            tokens.append({'t':'s', 'v': look})
            getChar()
    return tokens


def buildDictionary(tokens):
    dict = {}
    lastIdent=None
    for token in tokens:
        if token['t']=='n':
            lastIdent=token['v']
        elif token['t']=='s':
            if token['v']!='=':
                lastIdent=None
        elif lastIdent and (token['t']=='$' or token['t']=='i' or token['t']=='f'):
            dict[lastIdent]=token['v']
            lastIdent=None
        else:
            lastIdent=None
    return dict

#types
#s - symbol
#n - name
#i - int
#f - float
#$ - string

startTime = time.ticks_ms()
tokens = tokenize('<socket state=3 timeout=-1 incoming=2000fc0c off=0>')
dict=buildDictionary(tokens)
endTime = time.ticks_ms()
print(dict)
print(endTime-startTime)