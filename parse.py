import re

class ParseError(Exception):
    pass

#parsing inspired by jack crenshaws lets build a compiler

def tokenize(string):
    #i was using regular strings, but the b'' strings are like twice as performant
    if type(string) is str:
        string=string.encode()

    index=0

    #I had regexs for strings and white space manually parsing them is about as fast and less likely to break from lonnggg strings or whitespace
    number=re.compile(rb"([-+]?((\d+\.?\d*)|(\d*\.?\d+)))")
    ident=re.compile(rb"([a-zA-Z]+\d*[a-zA-Z0-9_]*)")
    symbol=re.compile(rb'([=\[\],;<>])')

    tokens=[]
    stringLen = len(string)
    
    while index<stringLen:

        if string[index]<=32 and string[index]!=0:
            start=index+1
            index+=1
            while index<stringLen and string[index]<=32 and string[index]!=0:
                index+=1
            tokens.append((b'white',))
            if index>=stringLen:
                break

        if string[index]==b'"'[0] or string[index]==b"'"[0]:
            stringStart=string[index]
            start=index+1
            index+=1
            if index>=stringLen:
                raise ParseError('Tokenize: failed to tokenize, unterminated string at index '+str(start)+":"+str(index))
            while string[index]!=stringStart:
                index+=1
                if index>=stringLen:
                    raise ParseError('Tokenize: failed to tokenize, unterminated string at index '+str(start)+":"+str(index))
            tokens.append((b'string', string[start:index]))
            index+=1
            continue

        match=number.match(string[index:])
        if match:
            num = match.group(1)
            if b'.' in num:
                tokens.append((b'number', float(num)))
            else:
                tokens.append((b'number', int(num)))
            index+=match.end(0)
            continue

        match=ident.match(string[index:])
        if match:
            tokens.append((b'name', match.group(1)))
            index+=match.end(0)
            continue

        match=symbol.match(string[index:])
        if match:
            tokens.append((b'symbol', match.group(1)))
            index+=match.end(0)
            continue

        break
    if index!=stringLen:
        raise ParseError('Tokenize: unexpected character at index: '+str(index)+', char: '+chr(string[index]))

    return tokens

def parse(inTokens):
    tokens=[]
    lastToken=None
    for token in inTokens:
        if lastToken and lastToken[0]==b'number' and token[0]==b'name':
            raise ParseError('invalid syntax, number:'+str(lastToken[1])+' followed immediately by name:'+str(token[1]))
        lastToken=token
        if token[0]!=b'white':
            tokens.append(token)
    tokens.append((b'end',))
    token=None
    tokenIndex = 0
    tokenEndIndex=len(tokens)

    def getToken():
        nonlocal tokenIndex, token, tokenEndIndex
        if tokenIndex<tokenEndIndex:
            token=tokens[tokenIndex]
            tokenIndex+=1
        else:
            token=None


    def matchSymbol(value=None):
        nonlocal token
        if token and token[0]==b'symbol':
            if value and token[1]!=value:
                raise ParseError('expected value of '+str(value)+' but found '+str(token[1]))
            getToken()
        else:
            raise ParseError('expected type of symbol but found '+(str(token[0]) if token else 'nothing'))
        
    def matchEnd():
        nonlocal token
        if not (token and token[0]==b'end'):
            raise ParseError('expected end of token but found '+(str(token[0]) if token else 'nothing'))
        
    def matchName():
        nonlocal token
        if token and token[0]==b'name':
            name=token[1]
            getToken()
            return name
        else:
            raise ParseError('expected type of name but found '+(str(token[0]) if token else 'nothing'))
        
    def matchValue():
        nonlocal token
        if token and token[0] in [b'name', b'string', b'number']:
            value=token[1]
            getToken()
            return value
        else:
            raise ParseError('expected type of name but found '+(str(token[0]) if token else 'nothing'))

    getToken()
    matchSymbol(b'<')
    objName=matchName()
    props={}
    while token and token[0] in [b'name']:
        prop=matchName()
        matchSymbol(b'=')
        value=matchValue()
        props[prop]=value
    matchSymbol(b'>')
    matchEnd()

    return objName, props

def compile(text):
    try:
        tokens=tokenize(text)
        obj=parse(tokens)
        return obj
    except ParseError as err:
        print("ParseError: ", err)
        return None
    