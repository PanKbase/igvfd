from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path
from pyramid.view import view_config
from .base import (
    Item,
)


@abstract_collection(
    name='donors',
    unique_key='accession',
    properties={
        'title': 'Donors',
        'description': 'Listing of donors',
    }
)
class Donor(Item):
    item_type = 'donor'
    base_types = ['Donor'] + Item.base_types
    name_key = 'accession'
    schema = load_schema('igvfd:schemas/donor.json')
    embedded_with_frame = [
        Path('award', include=['@id', 'component']),
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('phenotypic_features.feature', include=['@id', 'feature', 'term_id',
             'term_name', 'quantity', 'quantity_units', 'observation_date'])
    ]

    set_status_up = [
        'documents'
    ]
    set_status_down = []


@collection(
    name='human-donors',
    unique_key='accession',
    properties={
        'title': 'Human Donors',
        'description': 'Listing of human donors',
    }
)
class HumanDonor(Donor):
    item_type = 'human_donor'
    schema = load_schema('igvfd:schemas/human_donor.json')
    embedded_with_frame = Donor.embedded_with_frame + [
        Path('related_donors.donor', include=['@id', 'accession']),
    ]
    audit_inherit = [
        'related_donors.donor'
    ]
    set_status_up = Donor.set_status_up + []
    set_status_down = Donor.set_status_down + []

    def update(self, properties, sheets=None):
        # Migrate 'biological_sex' field to 'genetic_sex' before validation
        # This allows backward compatibility with clients that still send 'biological_sex'
        if 'biological_sex' in properties:
            properties['genetic_sex'] = properties['biological_sex']
            del properties['biological_sex']
        super().update(properties, sheets)


def transform_biological_sex_to_genetic_sex(context, request):
    """Validator to transform 'biological_sex' to 'genetic_sex' before validation."""
    if hasattr(request, 'json_body') and request.json_body:
        if 'biological_sex' in request.json_body:
            request.json_body['genetic_sex'] = request.json_body['biological_sex']
            del request.json_body['biological_sex']


@view_config(
    context=HumanDonor.Collection,
    permission='add',
    request_method='POST',
    validators=[transform_biological_sex_to_genetic_sex]
)
def human_donor_add(context, request):
    """Custom add view for HumanDonor that transforms biological_sex to genetic_sex."""
    from snovault.crud_views import collection_add
    return collection_add(context, request)

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the human donor.',
            'notSubmittable': True,
        }
    )
    def summary(self, ethnicities=None, sex=None, diabetes_status=None):
        ethnicities_phrase = ''
        sex_phrase = ''
        diabetes_status_phrase = ''
        if ethnicities:
            ethnicities_phrase = ', '.join(ethnicities)
        if sex and sex != 'unspecified':
            sex_phrase = sex
        if diabetes_status and diabetes_status:
            diabetes_status_phrase = ', '.join(diabetes_status)
        summary_phrase = ' '.join([x for x in [ethnicities_phrase, sex_phrase, diabetes_status_phrase] if x != '']).strip()
        if summary_phrase:
            return summary_phrase
        else:
            return self.uuid


def transform_biological_sex_to_genetic_sex(context, request):
    """Validator to transform 'biological_sex' to 'genetic_sex' before validation."""
    if hasattr(request, 'json_body') and request.json_body:
        if 'biological_sex' in request.json_body:
            request.json_body['genetic_sex'] = request.json_body['biological_sex']
            del request.json_body['biological_sex']


@view_config(
    context=HumanDonor.Collection,
    permission='add',
    request_method='POST',
    validators=[transform_biological_sex_to_genetic_sex]
)
def human_donor_add(context, request):
    """Custom add view for HumanDonor that transforms biological_sex to genetic_sex."""
    from snovault.crud_views import collection_add
    return collection_add(context, request)


@collection(
    name='rodent-donors',
    unique_key='accession',
    properties={
        'title': 'Rodent Donors',
        'description': 'Listing of rodent donors',
    }
)
class RodentDonor(Donor):
    item_type = 'rodent_donor'
    schema = load_schema('igvfd:schemas/rodent_donor.json')
    embedded_with_frame = Donor.embedded_with_frame + [
        Path('sources', include=['@id', 'title']),
    ]
    set_status_up = Donor.set_status_up + []
    set_status_down = Donor.set_status_down + []

    def unique_keys(self, properties):
        keys = super(RodentDonor, self).unique_keys(properties)
        if properties.get('rodent_identifier'):
            lab = properties.get('lab').split('/')[-1]
            value = f'{lab}:{properties.get("rodent_identifier")}'
            keys.setdefault('rodentdonor:lab_rodentid', []).append(value)
        else:
            value = u'{strain}/{sex}'.format(**properties)
            keys.setdefault('rodentdonor:strain_sex', []).append(value)
        return keys

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the rodent donor.',
            'notSubmittable': True,
        }
    )
    def summary(self, strain, sex=None):
        if sex and sex != 'unspecified':
            return f'{strain} {sex}'
        else:
            return strain
