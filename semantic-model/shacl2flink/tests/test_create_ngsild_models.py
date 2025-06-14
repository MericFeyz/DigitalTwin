#
# Copyright (c) 2022 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from unittest.mock import MagicMock, patch
import os
from rdflib import BNode, URIRef, XSD
import unittest
import create_ngsild_models
from create_ngsild_models import nullify


def test_nullify():
    field = MagicMock()
    field.toPython.return_value = 'field'
    result = create_ngsild_models.nullify(None)
    assert result == 'NULL'
    result = create_ngsild_models.nullify(field)
    assert result == "'field'"


@patch('create_ngsild_models.nullify')
@patch('create_ngsild_models.Graph')
@patch('create_ngsild_models.configs')
@patch('create_ngsild_models.utils')
def test_main(mock_utils, mock_configs, mock_graph, mock_nullify, tmp_path):
    def __add__(self, other):
        return self

    mock_nullify.return_value = 'nullify'
    mock_configs.iff_namespace = 'iff_namespace'
    mock_configs.attributes_table_name = 'attributes'
    mock_utils.strip_class.return_value = 'strip_class'
    mock_graph.__add__.return_value = mock_graph
    mock_graph.return_value = mock_graph
    mock_graph.__iadd__.return_value = mock_graph
    entityId = MagicMock()
    entityId.toPython.return_value = 'entityId'
    name = MagicMock()
    name.toPython.return_value = 'name'
    name.return_value = 'name'
    type = MagicMock()
    type.toPython.return_value = 'type'
    nodeType = MagicMock()
    nodeType.toPython.return_value = 'nodeType'
    valueType = MagicMock()
    valueType.toPython.return_value = 'valueType'
    hasValue = MagicMock()
    hasValue.toPython.return_value = 'hasValue'
    hasObject = MagicMock()
    hasObject.toPython.return_value = 'hasObject'
    hasValueList = MagicMock()
    hasValueList.toPython.return_value = 'hasValueList'
    hasJSON = MagicMock()
    hasJSON.toPython.return_value = 'hasJSON'
    observedAt = MagicMock()
    observedAt.toPython.return_value = 'Timestamp'
    index = MagicMock()
    index.toPython.return_value = 'index'
    unitCode = MagicMock()
    unitCode.toPython.return_value = 'unitCode'
    mock_graph.query.side_effect = [[
        (entityId, name, type, nodeType, valueType, hasValue, hasObject, hasValueList,
         hasJSON, observedAt, index, unitCode),
        (entityId, name, type, nodeType, valueType, hasValue, hasObject, hasValueList,
         hasJSON, observedAt, None, unitCode),
        (entityId, name, type, nodeType, valueType, hasValue, hasObject, hasValueList,
         hasJSON, observedAt, None, None)],
        [(entityId, type, name, type)]
    ]
    create_ngsild_models.main('kms/shacl.ttl', 'kms/knowledge.ttl',
                              'kms/model.jsonld', tmp_path)
    assert os.path.exists(os.path.join(tmp_path, 'ngsild-models.sqlite'))\
        is True


def test_get_entity_id_and_parentId():
    # Create a mock graph
    mock_graph = MagicMock()

    # Create test nodes and triples
    node = BNode()

    parent_node = BNode()

    grandparent_node = URIRef('urn:test:grendparent')

    predicate1 = URIRef('urn:test:2')

    predicate2 = URIRef('urn:test:3')

    # Mock the triples in the graph
    mock_graph.triples.side_effect = [
        iter([(parent_node, predicate1, node)]),  # First call returns a triple
        iter([(grandparent_node, predicate2, parent_node)]),  # Second call returns another triple
        iter([])  # No more triples for the third call
    ]
    mock_graph.objects.side_effect = [iter([]), iter([])]
    # Call the function
    result_id, result_entityId, result_parentId = create_ngsild_models.get_entity_id_and_parentId(
        node, 'test_name', None, mock_graph
    )

    # Verify the results
    assert result_id == 'urn:test:grendparent\\urn:test:3\\@none\\urn:test:2\\@none\\test_name\\@none'

    assert result_entityId == grandparent_node
    assert result_parentId == "'urn:test:grendparent\\urn:test:3\\@none\\urn:test:2\\@none'"

    # Verify the graph was traversed correctly
    assert mock_graph.triples.call_count == 2


def test_parser():
    args = create_ngsild_models.parse_args(['shaclfile.ttl', 'knowledge.ttl', 'model.jsonld'])
    assert args.shaclfile == 'shaclfile.ttl'
    assert args.knowledgefile == 'knowledge.ttl'
    assert args.modelfile == 'model.jsonld'


def test_add_or_get_index():
    # Create an instance of StringIndexer
    indexer = create_ngsild_models.StringIndexer()

    # Test adding a new id and string
    index = indexer.add_or_get_index("id1", "string1")
    assert index == 0  # First index should be 0
    assert indexer.id_to_index_map["id1"]["string_to_index"]["string1"] == 0

    # Test retrieving an existing string
    index = indexer.add_or_get_index("id1", "string1")
    assert index == 0  # Index should remain 0 for the same string

    # Test adding a new string under the same id
    index = indexer.add_or_get_index("id1", "string2")
    assert index == 1  # Next index should be 1
    assert indexer.id_to_index_map["id1"]["string_to_index"]["string2"] == 1

    # Test adding a new id and string
    index = indexer.add_or_get_index("id2", "string1")
    assert index == 0  # First index for a new id should be 0
    assert indexer.id_to_index_map["id2"]["string_to_index"]["string1"] == 0

    # Test retrieving an existing string under a different id
    index = indexer.add_or_get_index("id2", "string1")
    assert index == 0  # Index should remain 0 for the same string under the same id


class TestCreateNgsildModels(unittest.TestCase):

    def test_nullify(self):
        # Test nullify function
        self.assertEqual(nullify(None), 'NULL')
        self.assertEqual(nullify(XSD.string), "'http://www.w3.org/2001/XMLSchema#string'")


if __name__ == '__main__':
    unittest.main()
