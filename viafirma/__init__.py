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
        self.url = 'https://{}.viafirma.com/documents/api/v3/'.format(server)

    @property
    def is_sandbox(self):
        return SANDBOX == self.server

    def is_alive(self):
        url = '/'.join([self.url, 'system/alive'])
        return requests.get(url)

    def create_process(self, group_code, documents):
        pass

    def create_signature(self, group_code, document):
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
            "document": {
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
        }
        json_data["document"].update(document.serialize())
        return requests.post(
            url, json=json_data, auth=(self.user, self.password)
        ).json()

    def check_signature(self, code):
        """
        Check signature status
        :param code: signature code
        :type code: string
        :return: A signature status
        :rtype: dict
        """
        url = '/'.join([self.url, 'messages/status', code])
        return requests.get(url).json()

    def get_signature(self, code):
        """
        Get all signature details
        :param code: signature code
        :type code: string
        :return: A signature details
        :rtype: dict
        """
        url = '/'.join([self.url, 'messages', code])
        return requests.get(url).json()
