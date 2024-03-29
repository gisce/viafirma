# coding: utf-8
import requests


SANDBOX = 'sandbox'
PRODUCTION = 'services'


class Document(object):
    read_required = True
    template_type = None
    template_reference = None
    template_code = None
    
    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)

    def serialize(self):
        """
        :return: A document serialized in JSON
        :rtype: dict
        """
        return {
            "templateType": self.template_type,
            "templateReference": self.template_reference,
            "readRequired": self.read_required,
            "watermarkText": "Preview",
            "templateCode": self.template_code
        }


class Base64Document(Document):
    templateType = "base64"

    def __init__(self, content, **attrs):
        super(Base64Document, self).__init__(**attrs)
        self.content = content

    def serialize(self):
        result = super(Base64Document, self).serialize()
        result["templateReference"] = self.content
        return result


class ViaFirmaClient(object):
    def __init__(self, user, password, server=SANDBOX):
        self.server = server
        self.user = user
        self.password = password
        self.url = 'https://{}.viafirma.com/documents/api/v3'.format(server)
        self.session = requests.Session()
        self.session.auth = (user, password)

    @property
    def is_sandbox(self):
        return SANDBOX == self.server

    def is_alive(self):
        url = '/'.join([self.url, 'system/alive'])
        return self.session.get(url)

    def create_process(self, group_code, documents):
        """
        :param group_code: Group Code string
        :type group_code: string
        :param documents: Documents
        :type documents: Document[]
        :return: A dictionary with signature information
        :rtype: dict
        """
        url = '/'.join([self.url, 'set'])
        json_data = {
            "groupCode": group_code,
            "messages": [
                d.serialize() for d in documents
            ]
        }
        return self.session.post(
            url, json=json_data
        ).json()

    def create_signature(self, group_code, documents, recipients, configuration):
        """
        :param group_code: Group Code string
        :type group_code: string
        :param documents: List
        :type documents: List of Class Document
        :param recipients: List
        :type recipients: List of recipients
        :param configuration: Dictionary
        :type configuration: Dictionary of optional parameters
        :return: A dictionary with signature information
        :rtype: dict
        """
        url = '/'.join([self.url, 'set'])

        messages = []

        for document in documents:
            message = {
                "document": document['base64'].serialize(),
                "policies": [{
                    "evidences": [{
                        "type": "SIGNATURE"
                    }],
                    "signatures": [{
                        "type": "SERVER",
                        "typeFormatSign": "PADES_B"
                    }]
                }]
            }
            if configuration.get('callbackMails'):
                message['callbackMails'] = configuration['callbackMails']

            if document.get('coords'):
                message['policies'][0]['evidences'][0]['positions'] = []
                message['policies'][0]['evidences'][0]['positions'].append({})
                message['policies'][0]['evidences'][0]['positions'][0]['rectangle'] = document['coords']
                message['policies'][0]['evidences'][0]['positions'][0]['page'] = 1
            messages.append(message)

        json_data = {
            "groupCode": group_code,
            "workflow": {
                "type": "PRESENTIAL"
            },
            "recipients": recipients,
            "messages": messages
        }
        return self.session.post(
            url, json=json_data
        ).json()

    def create_single_signature(self, group_code, document):
        """
        :param group_code: Group Code string
        :type group_code: string
        :param document: Document
        :type document: Document
        :return: A dictionary with signature information
        :rtype: dict
        """
        url = '/'.join([self.url, 'message/dispatch'])
        json_data = {
            "groupCode": group_code,
            "workflow": {
                "type": "PRESENTIAL"
            },
            "notification": {
                "text": "1a linea",
                "detail": "2a linea"
            },
            "document": document.serialize(),
            "policies": [{
                "evidences": [{
                    "type": "SIGNATURE"
                }],
                "signatures": [{
                    "type": "SERVER",
                    "typeFormatSign": "PADES_B"
                }]
            }]
        }
        return self.session.post(
            url, json=json_data
        ).json()

    def check_single_signature(self, code):
        """
        Check signature status
        :param code: signature code
        :type code: string
        :return: A signature status
        :rtype: dict
        """
        url = '/'.join([self.url, 'messages/status', code])
        return self.session.get(url).json()

    def get_single_signature(self, code):
        """
        Get all signature details
        :param code: signature code
        :type code: string
        :return: A signature details
        :rtype: dict
        """
        url = '/'.join([self.url, 'messages', code])
        return self.session.get(url).json()

    def check_signature(self, code):
        """
        Get all signature details
        :param code: signature code
        :type code: string
        :return: A signature details
        :rtype: dict
        """
        url = '/'.join([self.url, 'set/summary', code])
        return self.session.get(url).json()

    def download_signed_document(self, document_id):
        """
        Download signature document
        :param document_id: document code
        :type document_id: string
        :return: A signature details
        :rtype: dict
        """
        url = '/'.join([self.url, 'documents/download/signed/', document_id])
        return self.session.get(url).json()

    def download_trail_document(self, document_id):
        """
        Download signature document
        :param document_id: document code
        :type document_id: string
        :return: A signature details
        :rtype: dict
        """
        url = '/'.join([self.url, 'documents/download/trail/', document_id])
        return self.session.get(url).json()
