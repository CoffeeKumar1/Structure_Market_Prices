import json
import re


def lambda_handler(event, context):
    pricePattern = r'\b\d+(?:\.\d+)?'
    commodityLinePattern = r'\b([A-Za-z]+\d*?)\s+'
    colon = ':'
    doublequotes = '"'
    openCurlyBrace = '{'
    closeCurlyBrace = '}'
    oneDigitPattern = r'\b\d{1}(?:\.\d+)?\b'
    twoDigitPattern = r'\b\d{2}(?:\.\d+)?\b'
    threeDigitPattern = r'\b\d{3}(?:\.\d+)?\b'
    fourDigitPattern = r'\b\d{4}(?:\.\d+)?\b'
    fiveDigitPattern = r'\b\d{5}(?:\.\d+)?\b'
    
    Digitpatterns = [
        r'\b\d{1}(?:\.\d+)?\b',
        r'\b\d{2}(?:\.\d+)?\b',
        r'\b\d{3}(?:\.\d+)?\b',
        r'\b\d{4}(?:\.\d+)?\b',
        r'\b\d{5}(?:\.\d+)?\b',
    ]
    def removeIrrelevantData(lines):
        return re.sub(r"^.*\n\*?COFFEE PRICES\*?\n|(\n\*?PEPPER\*?\n.*)$", "", lines, flags=re.DOTALL)

    def removePhNumbers(lines):
        return re.sub(r'\d{10}', '', lines).strip()

    def removeSpecialChars(line):
        lineWOSpecChars = re.sub(r'[^A-Za-z\d.]', ' ', line)
        return re.sub(' +', ' ', lineWOSpecChars.strip())

    def parseCurrentTrader(line):
        tradercodes = {
            'mourya': 'Mourya Coffee Halebelur Sakleshpur',
            'handi': 'Handi Coffee Links',
            'pattadur': 'Pattadur Coffee House',
            'jeelani': 'Jeelani Coffee Kushalnagara',
            'gain': 'Sakleshpur Gain',
            'kushalnagar w': 'Kushalnagar Western',
            'kushalnagar m': 'Kushalnagar Mountain Blue',
            'likitha': 'Kunnigenahalli Likitha',
            'mr stany': 'MR Stany Golden Coffee CKM',
            'suvarna coffee': 'Suvarna Coffee',
            'prem coffee tra': 'Prem Coffee Trading Balupet',
            'ganesh traders ponampet': 'Ganesh Traders Ponampet',
            'ckm sangam': 'CKM Sangam',
            'sargod coffee c': 'Sargod Coffee Cures',
            'balupet mass': 'Balupet Mass',
            'balupete coffee': 'Balupete Coffee',
            'mudeemane': 'Mudigere Mudeemane',
            'mpccw': 'MPCCW',
            'coffee international': 'Coffee International Price US Cents LB',
            'mudremane coffee s': 'Mudremane Coffee Spices Mudigere',
            'raw coffee': 'Raw Coffee Prices',
            'fruit coffee prices': 'Fruit Coffee Prices',
            'malnad coffee': 'Malnad Coffee and Spices',
            'best coffee ': 'Best Coffee Spice Mudigere',
            'mudigere malnad' : 'Mudigere Malnad'}
        for substring, code in tradercodes.items():
            if substring in line.lower():
                return code.strip()
            else:
                continue
        return line.strip()

    def traderCommodityPriceROW(line, trader):
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
        traderKV = openCurlyBrace + doublequotes + 'Trader' + doublequotes + colon + doublequotes + trader + doublequotes
        commodityKV = doublequotes + 'Commodity' + doublequotes + colon + doublequotes + commodity + doublequotes
        priceLowKV = doublequotes + 'PriceLow' + doublequotes + colon + doublequotes + prices[0] + doublequotes 
        priceHighKV = doublequotes + 'PriceHigh' + doublequotes + colon + doublequotes + prices[1] + doublequotes 
        RawPriceDataKV = doublequotes + 'RawPriceData' + doublequotes + colon + doublequotes + prices[2] + doublequotes + closeCurlyBrace
        return '\n'.join([traderKV, commodityKV, priceLowKV, priceHighKV,RawPriceDataKV])

    def extractCommodity(expandedLine):
        return ' '.join(re.findall(commodityLinePattern, expandedLine))

    def extractPrices(expandedLine):
        priceLow = ''
        priceHigh = ''

        OneDigitNumbers = re.findall(oneDigitPattern,   expandedLine)
        TwoDigitNumbers = re.findall(twoDigitPattern,   expandedLine)
        ThreeDigitNumbers = re.findall(threeDigitPattern, expandedLine)
        FourDigitNumbers = re.findall(fourDigitPattern,  expandedLine)
        FiveDigitNumbers = re.findall(fiveDigitPattern,  expandedLine)

        len_onedigit = len(OneDigitNumbers)
        len_twodigit = len(TwoDigitNumbers)
        len_threedigit = len(ThreeDigitNumbers)
        len_fourdigit = len(FourDigitNumbers)
        len_fivedigit = len(FiveDigitNumbers)

        AllNumbers = []
        for pattern in Digitpatterns:
            AllNumbers += re.findall(pattern, expandedLine)

        AllPriceRawData = '-'.join(AllNumbers)

         # Filter out empty strings
        AllNumbers = [num for num in AllNumbers if num]

        if len(AllNumbers) == 1:
            priceLow = AllNumbers[0]
            return [priceLow,priceHigh,AllPriceRawData]
        
        if len(AllNumbers) > 1:
            #10000 - 11000
            if len_fivedigit == 2: 
                priceHigh = max(FiveDigitNumbers) 
                priceLow = min(FiveDigitNumbers)
                return [priceLow,priceHigh,AllPriceRawData]
            #5000 - 5500
            if len_fourdigit == 2:
                priceHigh = max(FourDigitNumbers)
                priceLow = min(FourDigitNumbers)
                return [priceLow,priceHigh,AllPriceRawData]
            #9900-11000
            if len_fivedigit == 1 and len_fourdigit == 1: 
                priceLow = FourDigitNumbers[0]
                priceHigh = FiveDigitNumbers[0]
                return [priceLow,priceHigh,AllPriceRawData]     
            #250 26 11000
            if len_fivedigit == 1 and len_fourdigit == 0: 
                priceLow = FiveDigitNumbers[0]
                return [priceLow,priceHigh,AllPriceRawData]
            #250 26 6000
            if len_fourdigit == 1 and len_fivedigit == 0: 
                priceLow = FourDigitNumbers[0]
                return [priceLow,priceHigh,AllPriceRawData]
            if len_fourdigit == 0 and len_fivedigit == 0:
                if len_threedigit != 0:
                    #485 - 500
                    if len_threedigit == 2: 
                        priceHigh = max(ThreeDigitNumbers)
                        priceLow = min(ThreeDigitNumbers)
                        return [priceLow,priceHigh,AllPriceRawData]
                    #258
                    elif len_threedigit == 1:
                        priceLow = ThreeDigitNumbers[0]
                        return [priceLow,priceHigh,AllPriceRawData]

                if len_twodigit != 0:
                    #38-42
                    if len_twodigit == 2: #When 2 two digit number range exist, generally for fruit prices
                        priceHigh = max(TwoDigitNumbers)
                        priceLow = min(TwoDigitNumbers)
                        return [priceLow,priceHigh,AllPriceRawData]
                    elif len_twodigit == 1:
                        priceLow = TwoDigitNumbers[0]
                        return [priceLow,priceHigh,AllPriceRawData]

    def expandCommodityNames(line):
        pattern = r'\b(ac|ap|rc|rp|ac28|rc27)\s+'
        mapping = {'ac': 'Arabica Cherry ',
                   'ap': 'Arabica Parchment ',
                   'rc': 'Robusta Cherry ',
                   'rp': 'Robusta Parchment ',
                   'ac28': 'Arabica Cherry OT28 ',
                   'rc27': 'Robusta Cherry OT27 '}
        mappedline = re.sub(
            pattern, lambda match: mapping[match.group(1)], line.lower())
        return re.sub(' +', ' ', mappedline)

    def treatLines(lines):
        treatedLines = []
        unnecessary_terms = ['pepper']
        for line in lines.split('\n'):
            if not any(term in line.lower() for term in unnecessary_terms):
                woSpecChars = removeSpecialChars(line.strip())
                DDICRow = extDataAndBuildDDICs(woSpecChars.strip())
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
        json_str = '[{}]'.format(json_str)
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
    woPhNumbers = removePhNumbers(woIrrelevantData)
    wTreatedLines = treatLines(woPhNumbers)
    jsonLikelines = parseLikeJson(wTreatedLines)
    withRootKey = openCurlyBrace + doublequotes + 'Report' + \
        doublequotes + colon + jsonLikelines + closeCurlyBrace

    return {
        'statusCode': 200,
        'body': withRootKey
    }
