"""Tool definitions for Gemini function calling.

Based on Property Partners API v2 OpenAPI spec:
https://editor.scalar.com/@ppartners/apis/property-partners-api/2.0.0
"""

from google.genai import types

search_locations_tool = types.FunctionDeclaration(
    name="search_locations",
    description=(
        "Search for locations (communes, neighborhoods, regions, cities) to obtain their "
        "keyName, which is required to filter properties. Always call this first "
        "when the user mentions a location name like 'Las Condes', 'Providencia', etc."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "country_id": types.Schema(
                type=types.Type.STRING,
                description="Country code.",
                enum=["CL", "PE", "AR", "CO", "ES", "US", "UY", "DO"],
            ),
            "search": types.Schema(
                type=types.Type.STRING,
                description=(
                    "Location name to search for. Diacritic-insensitive, "
                    "prefix-matching, case-insensitive. e.g. 'las condes', 'providencia'."
                ),
            ),
            "location_type": types.Schema(
                type=types.Type.STRING,
                enum=[
                    "commune", "neighborhood", "region", "city",
                    "municipality", "district", "department", "province",
                    "state", "sector", "county",
                ],
                description="Type of location to search for. Use 'commune' for Chilean comunas.",
            ),
        },
        required=["search"],
    ),
)

list_properties_tool = types.FunctionDeclaration(
    name="list_properties",
    description=(
        "List available properties with optional filters. Use the keyName obtained "
        "from search_locations as location_key_name. Returns a paginated list with "
        "property summaries including price, bedrooms, size, and location."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "location_key_name": types.Schema(
                type=types.Type.STRING,
                description="Location key from search_locations, e.g. 'cl/region-metropolitana/las-condes'.",
            ),
            "property_type": types.Schema(
                type=types.Type.STRING,
                enum=[
                    "APARTMENT", "HOUSE", "HOUSE_INDEPENDENT", "HOUSE_PAIRED",
                    "HOUSE_TERRACED", "DUPLEX", "PENTHOUSE", "OFFICE",
                    "LAND", "FIELD", "LOCAL", "WAREHOUSE", "PARKING",
                    "CONDOMINIUM", "TOWNHOUSE", "OTHER",
                ],
                description="Type of property.",
            ),
            "operation": types.Schema(
                type=types.Type.STRING,
                enum=["SELL", "RENT"],
                description="Whether the property is for sale or rent.",
            ),
            "bedrooms_min": types.Schema(
                type=types.Type.INTEGER,
                description="Minimum number of bedrooms.",
            ),
            "bathrooms_min": types.Schema(
                type=types.Type.INTEGER,
                description="Minimum number of bathrooms.",
            ),
            "parkplaces_min": types.Schema(
                type=types.Type.INTEGER,
                description="Minimum number of parking spaces.",
            ),
            "price_max": types.Schema(
                type=types.Type.NUMBER,
                description="Maximum price. Requires currency_id to be set.",
            ),
            "currency_id": types.Schema(
                type=types.Type.STRING,
                enum=["UF", "CLP", "USD", "EUR"],
                description="Currency for price filter.",
            ),
            "build_size_min": types.Schema(
                type=types.Type.NUMBER,
                description="Minimum built area in m2.",
            ),
            "sort": types.Schema(
                type=types.Type.STRING,
                enum=["price_asc", "price_desc", "last_update", "last_published"],
                description="Sort order for results.",
            ),
        },
        required=[],
    ),
)

get_property_detail_tool = types.FunctionDeclaration(
    name="get_property_detail",
    description=(
        "Get the full details of a specific property by its ID. Use this when the "
        "user asks for more information about a particular property. Returns complete "
        "data including description, features, images, contact info, and location."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "property_id": types.Schema(
                type=types.Type.STRING,
                description="The unique ID of the property.",
            ),
        },
        required=["property_id"],
    ),
)

convert_currency_tool = types.FunctionDeclaration(
    name="convert_currency",
    description=(
        "Convert an amount between currencies. Useful when the user mentions prices "
        "in CLP (pesos chilenos) and you need to convert to UF to filter properties, "
        "or when you want to show a price in a different currency. "
        "Fixed rate: 1 UF = 40,000 CLP. Example: 2,000,000 CLP = 50 UF."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "amount": types.Schema(
                type=types.Type.NUMBER,
                description="The amount to convert.",
            ),
            "from_currency": types.Schema(
                type=types.Type.STRING,
                enum=["UF", "CLP"],
                description="Source currency.",
            ),
            "to_currency": types.Schema(
                type=types.Type.STRING,
                enum=["UF", "CLP"],
                description="Target currency.",
            ),
        },
        required=["amount", "from_currency", "to_currency"],
    ),
)

# Bundle all tools into a single Tool object for Gemini
property_tools = [
    types.Tool(function_declarations=[
        search_locations_tool,
        list_properties_tool,
        get_property_detail_tool,
        convert_currency_tool,
    ])
]
