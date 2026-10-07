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
    paths_filtered_by_status,
)
from igvfd.calculated.human_donor import (
    compute_aab_count,
    compute_aab_positive,
    compute_aab_summary,
    compute_aab_tested,
    compute_age_group,
    compute_dominant_genetic_ancestry,
    compute_grs2_normalized,
    compute_grs2_score,
    compute_label_hba1c_discordant,
    compute_pediatric,
    compute_sex_discordant,
    compute_t2d_grs_normalized,
    compute_t2d_grs_score,
    compute_tier1_complete,
    data_available_datasets,
    data_available_keys,
    data_available_tissues,
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
    # Reverse link so donor edits invalidate biosamples that list this donor.
    rev = {
        'biosamples': ('Biosample', 'donors'),
    }
    embedded_with_frame = [
        Path('award', include=['@id', 'component', 'title', 'name']),
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('phenotypic_features.feature', include=['@id', 'feature', 'term_id',
             'term_name', 'quantity', 'quantity_units', 'observation_date'])
    ]

    set_status_up = [
        'documents'
    ]
    set_status_down = []

    @calculated_property(schema={
        'title': 'Biosamples',
        'type': 'array',
        'description': 'Biosamples that list this donor.',
        'minItems': 1,
        'uniqueItems': True,
        'items': {
            'title': 'Biosample',
            'type': ['string', 'object'],
            'linkFrom': 'Biosample.donors',
        },
        'notSubmittable': True,
    })
    def biosamples(self, request, biosamples):
        return paths_filtered_by_status(request, biosamples)


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
        if 'other_theraphy' in properties:
            legacy = properties.pop('other_theraphy')
            if 'other_therapy' not in properties:
                properties['other_therapy'] = legacy
            elif isinstance(legacy, list) and isinstance(
                properties['other_therapy'], list
            ):
                for x in legacy:
                    if x and x not in properties['other_therapy']:
                        properties['other_therapy'].append(x)
        super().update(properties, sheets)

    @calculated_property(schema={
        'title': 'Data Available Keys',
        'description': 'Normalized dataset|tissue keys from data_available (scMultiome expands to snATACseq and scRNAseq).',
        'type': 'array',
        'uniqueItems': True,
        'items': {'type': 'string'},
        'notSubmittable': True,
    })
    def data_available_keys(self, data_available=None):
        keys = data_available_keys(data_available)
        return keys or None

    @calculated_property(schema={
        'title': 'Data Available Datasets',
        'description': 'Normalized dataset names from data_available (scMultiome expands to snATACseq and scRNAseq).',
        'type': 'array',
        'uniqueItems': True,
        'items': {'type': 'string'},
        'notSubmittable': True,
    })
    def data_available_datasets(self, data_available=None):
        values = data_available_datasets(data_available)
        return values or None

    @calculated_property(schema={
        'title': 'Data Available Tissues',
        'description': 'Normalized tissues from data_available.',
        'type': 'array',
        'uniqueItems': True,
        'items': {'type': 'string'},
        'notSubmittable': True,
    })
    def data_available_tissues(self, data_available=None):
        values = data_available_tissues(data_available)
        return values or None

    @calculated_property(schema={
        'title': 'Autoantibody Count',
        'description': 'Number of positive autoantibodies among GADA, IAA, IA2, and ZNT8.',
        'type': 'integer',
        'notSubmittable': True,
    })
    def aab_count(self, aab_gada=None, aab_iaa=None, aab_ia2=None, aab_znt8=None, **kwargs):
        props = {
            'aab_gada': aab_gada,
            'aab_iaa': aab_iaa,
            'aab_ia2': aab_ia2,
            'aab_znt8': aab_znt8,
        }
        # Only treat as tested when at least one key was submitted (present on properties).
        present = {k: v for k, v in props.items() if k in self.properties}
        return compute_aab_count(present)

    @calculated_property(schema={
        'title': 'Autoantibody Tested',
        'description': 'True when any autoantibody field is present.',
        'type': 'boolean',
        'notSubmittable': True,
    })
    def aab_tested(self, aab_gada=None, aab_iaa=None, aab_ia2=None, aab_znt8=None, **kwargs):
        present = {k: self.properties.get(k) for k in (
            'aab_gada', 'aab_iaa', 'aab_ia2', 'aab_znt8') if k in self.properties}
        return compute_aab_tested(present)

    @calculated_property(schema={
        'title': 'Autoantibody Positive',
        'description': 'True when aab_count > 0; omitted when not tested.',
        'type': 'boolean',
        'notSubmittable': True,
    })
    def aab_positive(self, aab_gada=None, aab_iaa=None, aab_ia2=None, aab_znt8=None, **kwargs):
        present = {k: self.properties.get(k) for k in (
            'aab_gada', 'aab_iaa', 'aab_ia2', 'aab_znt8') if k in self.properties}
        return compute_aab_positive(present)

    @calculated_property(schema={
        'title': 'Autoantibody Summary',
        'description': 'Short summary of positive autoantibodies (e.g. GADA+, IA2+).',
        'type': 'string',
        'notSubmittable': True,
    })
    def aab_summary(self, aab_gada=None, aab_iaa=None, aab_ia2=None, aab_znt8=None, **kwargs):
        present = {k: self.properties.get(k) for k in (
            'aab_gada', 'aab_iaa', 'aab_ia2', 'aab_znt8') if k in self.properties}
        return compute_aab_summary(present)

    @calculated_property(schema={
        'title': 'Age Group',
        'description': 'Age bin for filtering and faceting.',
        'type': 'string',
        'enum': ['0-12', '13-17', '18-39', '40-64', '65+'],
        'notSubmittable': True,
    })
    def age_group(self, age=None):
        return compute_age_group(age)

    @calculated_property(schema={
        'title': 'Pediatric',
        'description': 'True when age is under 18 years.',
        'type': 'boolean',
        'notSubmittable': True,
    })
    def pediatric(self, age=None):
        return compute_pediatric(age)

    @calculated_property(schema={
        'title': 'Sex Discordant',
        'description': 'True when gender and genetic_sex both present, not "-", and differ.',
        'type': 'boolean',
        'notSubmittable': True,
    })
    def sex_discordant(self, gender=None, genetic_sex=None):
        return compute_sex_discordant(gender, genetic_sex)

    @calculated_property(schema={
        'title': 'Label vs HbA1c Discordant',
        'description': 'True when diabetes_status_description conflicts with derived_diabetes_status.',
        'type': 'boolean',
        'notSubmittable': True,
    })
    def label_hba1c_discordant(self, diabetes_status_description=None, derived_diabetes_status=None):
        return compute_label_hba1c_discordant(diabetes_status_description, derived_diabetes_status)

    @calculated_property(schema={
        'title': 'Dominant Genetic Ancestry',
        'description': 'Highest-percentage genetic_ethnicities entry, or the sole entry when percentages are absent.',
        'type': 'string',
        'notSubmittable': True,
    })
    def dominant_genetic_ancestry(self, genetic_ethnicities=None):
        return compute_dominant_genetic_ancestry(genetic_ethnicities)

    @calculated_property(schema={
        'title': 'GRS2 Score',
        'type': 'number',
        'notSubmittable': True,
    })
    def grs2_score(self, genetic_risk_score=None):
        return compute_grs2_score(genetic_risk_score)

    @calculated_property(schema={
        'title': 'GRS2 Normalized Score',
        'type': 'number',
        'notSubmittable': True,
    })
    def grs2_normalized(self, genetic_risk_score=None):
        return compute_grs2_normalized(genetic_risk_score)

    @calculated_property(schema={
        'title': 'T2D GRS Score',
        'type': 'number',
        'notSubmittable': True,
    })
    def t2d_grs_score(self, genetic_risk_score=None):
        return compute_t2d_grs_score(genetic_risk_score)

    @calculated_property(schema={
        'title': 'T2D GRS Normalized Score',
        'type': 'number',
        'notSubmittable': True,
    })
    def t2d_grs_normalized(self, genetic_risk_score=None):
        return compute_t2d_grs_normalized(genetic_risk_score)

    @calculated_property(schema={
        'title': 'Tier 1 Complete',
        'description': 'True when all Tier 0 and Tier 1 fields are present.',
        'type': 'boolean',
        'notSubmittable': True,
    })
    def tier1_complete(self, **kwargs):
        return compute_tier1_complete(self.properties)


def transform_biological_sex_to_genetic_sex(context, request):
    """Validator to transform 'biological_sex' to 'genetic_sex' before validation."""
    if hasattr(request, 'json_body') and request.json_body:
        if 'biological_sex' in request.json_body:
            request.json_body['genetic_sex'] = request.json_body['biological_sex']
            del request.json_body['biological_sex']


def normalize_human_donor_payload(context, request):
    """Accept legacy misspelled key other_theraphy (maps to other_therapy)."""
    if hasattr(request, 'json_body') and request.json_body:
        body = request.json_body
        if 'other_theraphy' in body:
            legacy = body.pop('other_theraphy')
            if 'other_therapy' not in body:
                body['other_therapy'] = legacy
            elif isinstance(legacy, list) and isinstance(body['other_therapy'], list):
                for x in legacy:
                    if x and x not in body['other_therapy']:
                        body['other_therapy'].append(x)


@view_config(
    context=HumanDonor.Collection,
    permission='add',
    request_method='POST',
    validators=[
        transform_biological_sex_to_genetic_sex,
        normalize_human_donor_payload,
    ]
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
            value = f'{lab}:{properties.get('rodent_identifier')}'
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
