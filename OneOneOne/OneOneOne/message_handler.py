from lxml import etree, objectify
import xml.etree.ElementTree as ET

from builder.pystache_message_builder import PystacheMessageBuilder
from utilities.file_utilities import FileUtilities
from definitions import XML_PATH, TEMPLATE_PATH
import logging

basic_success_response = FileUtilities.get_file_string(XML_PATH / 'basic_success_response.xml')

base_fault_response = FileUtilities.get_file_string(XML_PATH / 'basic_fault_response.xml')


def build_error_message(error):
    builder = PystacheMessageBuilder(str(TEMPLATE_PATH), 'base_error_template')
    return builder.build_message({"errorMessage": error})


class MessageHandler:
    namespaces = {
        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        'a': 'http://www.etis.fskab.se/v1.0/ETISws',
        'wsa': 'http://www.w3.org/2005/08/addressing',
        'itk': 'urn:nhs-itk:ns:201005'
    }

    def __init__(self, message_string):
        logging.basicConfig(level=logging.DEBUG)
        self.message = message_string
        self.message_tree = ET.fromstring(self.message)

        self.check_list = [
            self.check_action_types,
            self.check_manifest_and_payload_count,
            self.check_manifest_count_against_actual,
            self.check_payload_count_against_actual,
            self.check_payload_id_matches_manifest_id
        ]

    def evaluate_message(self):
        """
        This iterates over the message check methods searching for errors in the message, if no errors are found
        a success response is returned

        :return:
        """
        for check in self.check_list:
            status, response = check()
            if status != 200:
                return status, response

        return 200, basic_success_response

    def check_action_types(self):
        """
        This method checks for equality between the action type in the header, and the service value in the message
        body as per the 'DE_INVSER' requirement specified in the requirements spreadsheet
        :return: status code, response content
        """
        action = ""
        for type_tag in self.message_tree.findall("./soap:Header"
                                                  "/wsa:Action",
                                                  self.namespaces):
            action = type_tag.text

        service = ""
        for type_tag in self.message_tree.findall('./soap:Body'
                                                  '/itk:DistributionEnvelope'
                                                  '/itk:header',
                                                  self.namespaces):
            service = type_tag.attrib['service']

        if action != service:
            logging.warning("Action type does not match service type: (Action, Service) (%s, %s)", action,
                            service)
            return 500, build_error_message("Manifest action does not match service action")

        return 200, basic_success_response

    def check_manifest_and_payload_count(self):
        """
        This verifies the manifest count is equal to the payload count as per 'DE_INVMPC' requirement
        :return:
        """

        manifest_count = self.get_manifest_count()

        payload_count = self.get_payload_count()

        if payload_count != manifest_count:
            logging.warning("Error in manifest count: (ManifestCount, PayloadCount) (%s, %s)", manifest_count,
                            payload_count)
            return 500, build_error_message("Manifest count does not match payload count")

        return 200, basic_success_response

    def check_manifest_count_against_actual(self):
        """
        Checks if the manifest.count attribute matches the number of manifest items as per the 'DE_INVMCT'
        spec
        :return:
        """
        manifest_count = int(self.get_manifest_count())

        manifest_actual_count = len(self.message_tree.findall("./soap:Body"
                                                              "/itk:DistributionEnvelope"
                                                              "/itk:header"
                                                              "/itk:manifest"
                                                              "/itk:manifestitem",
                                                              self.namespaces))
        if manifest_count != manifest_actual_count:
            logging.warning("Manifest count did not equal number of instances: (expected : found) - (%i : %i)",
                            manifest_count, manifest_actual_count)

            return 500, build_error_message("The number of manifest instances does"
                                            " not match the manifest count specified")

        return 200, basic_success_response

    def check_payload_count_against_actual(self):
        """
        Checks if the specified payload count matches the actual occurrences of payload elements
        as per 'DE_INVPCT' in the spec
        :return:
        """
        payload_count = int(self.get_payload_count())

        payload_actual_count = len(self.message_tree.findall("./soap:Body"
                                                             "/itk:DistributionEnvelope"
                                                             "/itk:payloads"
                                                             "/itk:payload",
                                                             self.namespaces))
        if payload_count != payload_actual_count:
            logging.warning("Payload count does not match number of instaces - Expected: %i Found: %i",
                            payload_count,
                            payload_actual_count)
            return 500, base_fault_response

        return 200, basic_success_response

    def check_payload_id_matches_manifest_id(self):
        """
        Checks that for each id of each manifest item has a corrosponding
        payload with the same Id as per  'DE_INVMPI'
        :return: status code, xml response
        """
        payload_ids = set()
        manifest_ids = set()
        for payload in self.message_tree.findall("./soap:Body"
                                                 "/itk:DistributionEnvelope"
                                                 "/itk:payloads"
                                                 "/itk:payload",
                                                 self.namespaces):
            payload_ids.add(payload.attrib['id'])

        for manifest in self.message_tree.findall("./soap:Body"
                                                  "/itk:DistributionEnvelope"
                                                  "/itk:header"
                                                  "/itk:manifest"
                                                  "/itk:manifestitem",
                                                  self.namespaces):
            manifest_ids.add(manifest.attrib['id'])

        if len(payload_ids.difference(manifest_ids)) != 0:
            logging.warning("Payload IDs do not match Manifest IDs")
            return 500, build_error_message("Payload IDs do not map to Manifest IDs")

        return 200, basic_success_response

    def get_manifest_count(self):
        manifests = self.message_tree.findall("./soap:Body"
                                              "/itk:DistributionEnvelope"
                                              "/itk:header"
                                              "/itk:manifest",
                                              self.namespaces)

        if len(manifests) > 1:
            logging.warning("More than one manifest tag")

        return manifests[0].attrib['count']

    def get_payload_count(self):
        payloads = self.message_tree.findall("./soap:Body"
                                            "/itk:DistributionEnvelope"
                                            "/itk:payloads",
                                            self.namespaces)
        if len(payloads) > 1:
            logging.warning("Number of payloads tags greater than 1")
        payload_count = payloads[0].attrib['count']
        return payload_count
