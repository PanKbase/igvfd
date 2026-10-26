import pytest


def test_post_bad_lab(testapp, pi):
    testapp.post_json(
        '/lab',
        {
            'name': 'bad-lab',
            'institute_label': 'Stanford'
        },
        status=422)


def test_post_lab_with_consortium_name_and_no_pi(testapp):
    testapp.post_json(
        '/lab',
        {
            'name': 'consortium-lab',
            'institute_label': 'Stanford',
            'consortium_name': 'Example Consortium'
        },
        status=201)


def test_post_lab_with_pi_and_consortium_name(testapp, pi):
    testapp.post_json(
        '/lab',
        {
            'name': 'pi-and-consortium-lab',
            'institute_label': 'Stanford',
            'pi': pi['@id'],
            'consortium_name': 'Example Consortium'
        },
        status=201)


def test_post_lab_with_empty_consortium_name(testapp):
    testapp.post_json(
        '/lab',
        {
            'name': 'empty-consortium-lab',
            'institute_label': 'Stanford',
            'consortium_name': ''
        },
        status=422)
