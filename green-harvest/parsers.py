import re, pyexcel

def generic_parse(worksheet):
    data = [];
    headers = []
    rows = worksheet.rows
    for row in rows:
        row = list(map(lambda c: c.value, row))
        if row[0] == None:
            continue
        if headers == []:
            headers = row
        else:
            data.append(row)
    return headers, data


class ColoradoDocumentParser:
    class UnknownDocumentException(Exception):
        pass

    # Docname, Patterns, Sheet, HeaderRow, Headers
    file_data = (
        ("Recreational Transporter", r"^RTransporter", "Sheet1", 1, -2,
         ["LICENSEE", "DBA", "LICENSE #", "STREET ADDRESS", "CITY", "ZIP"]),

        ("Medicinal Transporter", r"^M[-\s]?Transporter", "Sheet1", 1, -2,
         ["LICENSEE", "DBA", "LICENSE #", "STREET ADDRESS", "CITY", "ZIP"]),

        # ("Recreational Lab", r"^RLab"),
        # ("Medicinal Lab", r"^MLab"),

        ("Recreational Retail Operators", r"^ROperator", "Sheet1", 1, -2,
         ["LICENSEE", "DBA", "LICENSE #", "STREET ADDRESS", "CITY", "ZIP"]),

        ("Medicinal Retail Operators", r"^MOperators", "Sheet1", 1, -2,
         ["LICENSEE", "DBA", "LICENSE #", "STREET ADDRESS", "CITY", "ZIP"]),

        ("Product Manufacturers", r"^Product", "Sheet1", 1, -2,
         ["LICENSEE", "DBA", "LICENSE #", "STREET ADDRESS", "CITY", "ZIP"]),

        ("Marijuana Infused Product Manufacturers", r"^MIPs", "Sheet1", 1, -2,
         ["LICENSEE", "DBA", "LICENSE #", "STREET ADDRESS", "CITY", "ZIP"]),

        ("Recreational Growers", r"^RGrows", "Sheet1", 1, -2,
         ["LICENSEE", "DBA", "LICENSE #", "STREET ADDRESS", "CITY", "ZIP"]),

        ("Medicinal Growers", r"^MGrows", "Sheet1", 1, -2,
         ["LICENSEE", "DBA", "LICENSE #", "STREET ADDRESS", "CITY", "ZIP"]),

        ("Stores", r"^Stores", "Sheet1", 1, -2,
         ["LICENSEE", "DBA", "LICENSE #", "STREET ADDRESS", "CITY", "ZIP"]),

        ("Centers", r"^Center", "Sheet1", 1, -2,
         ["LICENSEE", "DBA", "LICENSE #", "STREET ADDRESS", "CITY", "ZIP"]),
    )

    @classmethod
    def filetype_from_filename(cls, filename):
        '''returns the identity of the file based on parsing the filename'''
        filetype = None
        for pattern in cls.file_data:
            if re.search(pattern[1], filename):
                filetype = pattern[0]
        return filetype

    def __init__(self, file, filename):
        filetype = self.filetype_from_filename(filename)
        if filetype is None:
            raise self.UnknownDocumentException
        self.filename = filename
        self.file = file
        self.data = next(filter(lambda f: f[0] == filetype, self.file_data))
        self.document = self.load_document()

    def load_document(self):
        '''Opens up the document in the correct library for reading'''
        extension = self.filename.split(".")[-1]
        document = pyexcel.get_book(file_type=extension, file_stream=self.file)[self.data[2]]
        return document


    def get_headers(self):
        '''
        returns an array with the header names
        '''
        headers = list(map(lambda c: c.strip(), self.document[self.data[3]]))
        if headers != self.data[-1]:
            raise Exception("Unexpected Header Mismatch")
        return headers

    def get_data(self):
        '''
        Returns a python array-of-arrays filled with the data rows. 
        It loads into mem, but shouldn't be a problem unless millions of canna licenses get issued suddenly
        '''
        return self.document.array[self.data[3]+1:self.data[4]]

