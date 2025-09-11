import xml.dom.minidom as minidom
import xml.sax
import xml.sax.handler

def save_to_xml(data, filename):
    doc = minidom.Document()
    root = doc.createElement("BankAccounts")
    doc.appendChild(root)

    for record in data:
        account = doc.createElement("Account")
        fields = ['surname', 'name', 'patronymic', 'account_number', 'registration_address', 'mobile_phone', 'landline_phone']
        for i, value in enumerate(record):
            field = doc.createElement(fields[i])
            if value is not None:
                field.appendChild(doc.createTextNode(str(value)))
            account.appendChild(field)
        root.appendChild(account)

    with open(filename, 'w', encoding='utf-8') as f:
        doc.writexml(f, indent="  ", addindent="  ", newl="\n", encoding='utf-8')

class XMLHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.records = []
        self.current_record = {}
        self.current_field = None
        self.current_value = ""

    def startElement(self, name, attrs):
        if name != "BankAccounts" and name != "Account":
            self.current_field = name

    def characters(self, content):
        self.current_value += content

    def endElement(self, name):
        if self.current_field:
            self.current_record[self.current_field] = self.current_value.strip() if self.current_value.strip() else None
            self.current_value = ""
            self.current_field = None
        if name == "Account":
            record = (
                self.current_record.get('surname', ''),
                self.current_record.get('name', ''),
                self.current_record.get('patronymic', ''),
                int(self.current_record['account_number']) if self.current_record.get('account_number') else None,
                self.current_record.get('registration_address', ''),
                self.current_record.get('mobile_phone', ''),
                self.current_record.get('landline_phone', '')
            )
            self.records.append(record)
            self.current_record = {}

def load_from_xml(filename):
    handler = XMLHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse(filename)
    return handler.records