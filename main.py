import time

def isdigit(c):
    return c>=48 and c<=57
def isalpha(c):
    return (c>=97 and c<=122) or (c>=65 and c<=90)
def isalnum(c):
    return (c>=97 and c<=122) or (c>=65 and c<=90) or (c>=48 and c<=57)
def ishex(c):
    return (c>=48 and c<=57) or (c>=97 and c<=102) or (c>=65 and c<=70)

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
            look=b''

    def peek():
        nonlocal lookIndex
        peekIndex = lookIndex + 1
        if peekIndex>=len(text):
            return b''
        return text[peekIndex]

    def skipWhite():
        nonlocal look
        while look<=32:
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
                    tokens.append({b't':b'n', b'v': text[startIndex:lookIndex]})

        elif look==48 and (peek()==120 or peek()==88):#hex int
            getChar()
            getChar()
            startIndex=lookIndex
            if not ishex(look):
                raise ValueError('bad hex literal')
            while ishex(look):
                getChar()
                
            tokens.append({b't':b'i', b'v': int(text[startIndex:lookIndex], 16)})

        elif look==b'-' or look==b'+' or look==b'.' or isdigit(look):#ints, floats, or + - .
            unary=b''
            if look==b'-' or look==b'+':
                unary=look
                getChar()
                skipWhite()
            if not look or not (look==b'.' or isdigit(look)):
                tokens.append({b't':b's', b'v': unary})
            else:
                startIndex=lookIndex
                hasDec=False
                notDone=True
                while look and notDone:
                    notDone=False
                    if isdigit(look):
                        notDone=True
                    elif look==b'.' and not hasDec:
                        hasDec=True
                        notDone=True
                    if notDone:
                        getChar()
                if lookIndex-startIndex==1 and text[startIndex]==b'.':
                    if unary:
                        tokens.append({b't':b's', b'v': unary})
                    tokens.append({b't':b's', b'v': b'.'})
                else:
                    if hasDec:
                        val=float(text[startIndex:lookIndex])
                        if unary==b'-':
                            val=-val
                        tokens.append({b't':b'f', b'v': val})
                    else:
                        val=int(text[startIndex:lookIndex])
                        if unary==b'-':
                            val=-val
                        tokens.append({b't':b'i', b'v': val})
            
        elif look==b'"' or look==b"'":#strings
            toMatch = look
            getChar()
            startIndex=lookIndex
            while look and look!=toMatch:
                getChar()
            if look!=toMatch:
                raise ValueError('bad string literal')
            else:
                tokens.append({b't':b'$', b'v': text[startIndex:lookIndex]})
                getChar()

        else:#symbols
            tokens.append({b't':b's', b'v': look})
            getChar()
    return tokens


def buildDictionary(tokens):
    dict = {}
    lastIdent=None
    for token in tokens:
        if token[b't']==b'n':
            lastIdent=token[b'v']
        elif token[b't']==b's':
            if token[b'v']!=ord(b'='):
                lastIdent=None
        elif lastIdent and (token[b't']=='$' or token[b't']==b'i' or token[b't']==b'f'):
            dict[lastIdent]=token[b'v']
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
tokens = tokenize(b'state=3 timeout=-1 incoming=0x2000fc0c off=0 data="asdflkjasdf asdfkj asd fjakjsadf asjf asldf jasflkjadf askdjf asd0fas0df 98asd0f98 as9fd 8asdf9 8asd0f98 as09f 8asd f8a sa9 df8a0s9f 8as90f8 asdfl jkasdf as09f 8as09f8 asdf9 8as09f 8as0df9 8asd0f 98as09fd 8as09f8 asf 8asdf as asd fasdf 908as09f8as 98fa sdf08asd f09asdf asdjf l3 345j3k4h5 23kj5hjkdfkjgh sfgkj hsfgkjhsfgksdfgsfg8s dfg8sfgs8dfg sdfg7 sdf9gs98fg6 fasdflkjasdf asdfkj asd fjakjsadf asjf asldf jasflkjadf askdjf asd0fas0df 98asd0f98 as9fd 8asdf9 8asd0f98 as09f 8asd f8a sa9 df8a0s9f 8as90f8 asdfl jkasdf as09f 8as09f8 asdf9 8as09f 8as0df9 8asd0f 98as09fd 8as09f8 asf 8asdf as asd fasdf 908as09f8as 98fa sdf08asd f09asdf asdjf l3 345j3k4h5 23kj5hjkdfkjgh sfgkj hsfgkjhsfgksdfgsfg8s dfg8sfgs8dfg sdfg7 sdf9gs98fg6 f"')
dict=buildDictionary(tokens)
endTime = time.ticks_ms()
print(dict)
print(endTime-startTime)