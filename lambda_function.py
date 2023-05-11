import json,re

def lambda_handler(event, context):
    pricePattern = r'\b\d+(?:\.\d+)?'
    #traderPattern = r'\d+'
    commodityLinePattern = r'\b([A-Za-z]+\d*?)\s+' 
    colon = ':'
    doublequotes = '"'
    openCurlyBrace = '{'
    closeCurlyBrace = '}'
    def removeIrrelevantData(lines):
        return re.sub(r"^.*\n\*?COFFEE PRICES\*?\n|(\n\*?PEPPER\*?\n.*)$","", lines, flags=re.DOTALL)
    
    def removePhNumbers(lines):
        return re.sub(r'\d{10}', '', lines).strip()
    
    def removeSpecialChars(line):
        lineWOSpecChars = re.sub(r'[^A-Za-z\d.]',' ',line)
        return re.sub(' +', ' ', lineWOSpecChars.strip())
    
    def parseCurrentTrader(line):
        tradercodes = {
            'mourya'               : 'Mourya Coffee Halebelur Sakleshpur',
            'handi'                : 'Handi Coffee Links',
            'pattadur'             : 'Pattadur Coffee House',
            'jeelani'              : 'Jeelani Coffee Kushalnagara',
            'gain'                 : 'Sakleshpur Gain',
            'kushalnagar'          : 'Kushalnagar Western',
            'likitha'              : 'Kunnigenahalli Likitha',
            'mr stan'              : 'MR Stany Golden Coffee CKM',
            'suvarna'              : 'Suvarna Coffee',
            'prem'                 : 'Prem Coffee Trading Balupet',
            'ganesh'               : 'Ganesh Traders Ponampet',
            'ckm s'                : 'CKM Sangam',
            'sargod'               : 'Sargod Coffee Cures',
            'balupet'              : 'Balupet Mass',
            'mudeemane'            : 'Mudigere Mudeemane',
            'mpccw'                : 'MPCCW',
            'coffee international' : 'Coffee International Price US Cents LB',
            'mudremane'            : 'Mudremane Coffee Spices Mudigere',
            'raw coffee'           : 'Raw Coffee Prices',
            'fruit coffee prices'  : 'Fruit Coffee Prices',
            'malnad coffee'        : 'Malnad Coffee and Spices' }
        for substring, code in tradercodes.items():
            if substring in line.lower():
                return code.strip()
            else:
                continue
        return line.strip()
            
    def traderCommodityPriceROW(line,trader):
        expandedCommodityNames = expandCommodityNames(line)
        prices = extractPrices(expandedCommodityNames)
        commodity = extractCommodity(expandedCommodityNames)
        return buildKeyValue(trader, prices, commodity)

    currenttrader = ''
    def extDataAndBuildDDICs(line):
        global currenttrader 
        if isTrader(line):
           currenttrader = parseCurrentTrader(line) 
           return ''
        elif isCommodityAndPrice(line):
            return traderCommodityPriceROW(line, currenttrader)
        
    def isCommodityAndPrice(line):
        return len(re.findall(pricePattern, line)) != 0
    
    def isTrader(line):
        return len(re.findall(pricePattern, line)) == 0
    
    def buildKeyValue(trader, prices, commodity):
        traderKV    = openCurlyBrace + doublequotes + 'Trader' + doublequotes + colon + doublequotes + trader + doublequotes
        commodityKV = doublequotes + 'Commodity' + doublequotes + colon + doublequotes + commodity + doublequotes
        priceKV     = doublequotes + 'Price' + doublequotes + colon + doublequotes + prices + doublequotes +closeCurlyBrace
        return '\n'.join([traderKV,commodityKV,priceKV])
    
    def extractCommodity(expandedLine):
        return ' '.join(re.findall(commodityLinePattern,expandedLine))
    
    def extractPrices(expandedLine):
        return '-'.join(re.findall(pricePattern, expandedLine))
    
    def expandCommodityNames(line):
        pattern = r'\b(ac|ap|rc|rp|ac28|rc27)\s+'
        mapping = { 'ac'  : 'Arabica Cherry ',
                    'ap'  : 'Arabica Parchment ',
                    'rc'  : 'Robusta Cherry ',
                    'rp'  : 'Robusta Parchment ',
                    'ac28': 'Arabica Cherry OT28 ',
                    'rc27': 'Robusta Cherry OT27 '}
        mappedline = re.sub(pattern, lambda match: mapping[match.group(1)], line.lower())
        return re.sub(' +', ' ', mappedline)
    
    def treatLines(lines):
        treatedLines = []
        unnecessary_terms = ['pepper']
        for line in lines.split('\n'):
            if not any(term in line.lower() for term in unnecessary_terms):
                woSpecChars = removeSpecialChars(line.strip())
                DDICRow     = extDataAndBuildDDICs(woSpecChars.strip())
                treatedLines.append(DDICRow)
        return '\n'.join(treatedLines)
    
    def parseLikeJson(lines):
        json_str = replNewlineWcommas(lines)   
        json_str = RCBefClosingCurlyBrace(json_str)  
        json_str = RCAftOpenCurlyBrace(json_str)  
        json_str = RCBefClosingSqBracket(json_str) 
        json_str = RCAftOpeningSqBracket(json_str) 
        json_str = remCommBetCloBraceNCloSqBracket(json_str)
        json_str = json_str.rstrip(',')            
        json_str =  '[{}]'.format(json_str)
        json_str = RCBefClosingSqBracket(json_str) 
        json_str = RCAftOpeningSqBracket(json_str)
        return json_str

    def remCommBetCloBraceNCloSqBracket(json_str):
        json_str = re.sub(r'},\s*\],', '}]', json_str)
        return json_str

    def RCAftOpeningSqBracket(json_str):
        json_str = re.sub(r'\[\s*,', '[', json_str)
        return json_str

    def RCBefClosingSqBracket(json_str):
        json_str = re.sub(r',\s*\]', ']', json_str)
        return json_str

    def RCAftOpenCurlyBrace(json_str):
        json_str = re.sub(r'{\s*,', '{', json_str)
        return json_str

    def RCBefClosingCurlyBrace(json_str):
        json_str = re.sub(r',\s*}', '}', json_str)
        return json_str

    def replNewlineWcommas(lines):
        json_str = re.sub(r'\n\s*', ',\n', lines)
        return json_str

    woIrrelevantData = removeIrrelevantData(event['message'])
    woPhNumbers      = removePhNumbers(woIrrelevantData)
    wTreatedLines    = treatLines(woPhNumbers)
    jsonLikelines    = parseLikeJson(wTreatedLines)
    withRootKey      = openCurlyBrace + doublequotes +'Report' + doublequotes + colon + jsonLikelines + closeCurlyBrace
    
    return {
        'statusCode': 200,
        'body': withRootKey
    }
