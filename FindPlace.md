Find Place 

bookmark_border

Note: Server-side and client-side libraries
A Find Place request takes a text input and returns a place. The input can be any kind of Places text data, such as a name, address, or phone number. The request must be a string. A Find Place request using non-string data such as a lat/lng coordinate or plus code generates an error.

A Find Place request returns a subset of the fields that are returned by a Place Details request. For more information on the fields that are unavailable in a Find Place request, see Places API fields support. If the field you want is not returned, you can use Find Place to get a place_id, then use that ID to make a Place Details request.
Find Place requests
A Find Place request is an HTTP URL of the following form:


https://maps.googleapis.com/maps/api/place/findplacefromtext/output?parameters
where output may be either of the following values:

json (recommended) indicates output in JavaScript Object Notation (JSON)
xml indicates output as XML
Certain parameters are required to initiate a Find Place request. As is standard in URLs, all parameters are separated using the ampersand (&) character.

Required parameters
input
The text string on which to search, for example: "restaurant" or "123 Main Street". This must be a place name, address, or category of establishments. Any other types of input can generate errors and are not guaranteed to return valid results. The Places API will return candidate matches based on this string and order the results based on their perceived relevance.

inputtype
The type of input. This can be one of either textquery or phonenumber. Phone numbers must be in international format (prefixed by a plus sign ("+"), followed by the country code, then the phone number itself). See E.164 ITU recommendation for more information.

Optional parameters
fields
Caution: Place Search requests and Place Details requests do not return the same fields. Place Search requests return a subset of the fields that are returned by Place Details requests. If the field you want is not returned by Place Search, you can use Place Search to get a place_id, then use that Place ID to make a Place Details request. For more information on the fields that are unavailable in a Place Search request, see Places API fields support.
Use the fields parameter to specify a comma-separated list of place data types to return. For example: fields=formatted_address,name,geometry. Use a forward slash when specifying compound values. For example: opening_hours/open_now.

Fields are divided into three billing categories: Basic, Contact, and Atmosphere. Basic fields are billed at base rate, and incur no additional charges. Contact and Atmosphere fields are billed at a higher rate. See the pricing sheet for more information. Attributions, html_attributions, are always returned with every call, regardless of whether the field has been requested.

Basic

The Basic category includes the following fields: address_components, adr_address, business_status, formatted_address, geometry, icon, icon_mask_base_uri, icon_background_color, name, permanently_closed (deprecated), photo, place_id, plus_code, type, url, utc_offset, vicinity, wheelchair_accessible_entrance.

Contact

The Contact category includes the following fields: current_opening_hours, formatted_phone_number, international_phone_number, opening_hours, secondary_opening_hours, website

Atmosphere

The Atmosphere category includes the following fields: curbside_pickup, delivery, dine_in, editorial_summary, price_level, rating, reservable, reviews, serves_beer, serves_breakfast, serves_brunch, serves_dinner, serves_lunch, serves_vegetarian_food, serves_wine, takeout, user_ratings_total.

language
The language in which to return results.

See the list of supported languages. Google often updates the supported languages, so this list may not be exhaustive.
If language is not supplied, the API attempts to use the preferred language as specified in the Accept-Language header.
The API does its best to provide a street address that is readable for both the user and locals. To achieve that goal, it returns street addresses in the local language, transliterated to a script readable by the user if necessary, observing the preferred language. All other addresses are returned in the preferred language. Address components are all returned in the same language, which is chosen from the first component.
If a name is not available in the preferred language, the API uses the closest match.
The preferred language has a small influence on the set of results that the API chooses to return, and the order in which they are returned. The geocoder interprets abbreviations differently depending on language, such as the abbreviations for street types, or synonyms that may be valid in one language but not in another. For example, utca and tér are synonyms for street in Hungarian.
locationbias
Prefer results in a specified area, by specifying either a radius plus lat/lng, or two lat/lng pairs representing the points of a rectangle. If this parameter is not specified, the API uses IP address biasing by default.

IP bias: Instructs the API to use IP address biasing. Pass the string ipbias (this option has no additional parameters).
Circular: A string specifying radius in meters, plus lat/lng in decimal degrees. Use the following format: circle:radius@lat,lng.
Rectangular: A string specifying two lat/lng pairs in decimal degrees, representing the south/west and north/east points of a rectangle. Use the following format:rectangle:south,west|north,east. Note that east/west values are wrapped to the range -180, 180, and north/south values are clamped to the range -90, 90.
Note: If you omit the fields parameter from a Find Place request, only the place_id for the result will be returned.
Find Place examples
The following example shows a Find Place request for "Museum of Contemporary Art Australia", including the photos, formatted_address, name, rating, opening_hours, and geometry fields:

URL
cURL

https://maps.googleapis.com/maps/api/place/findplacefromtext/json
  ?fields=formatted_address%2Cname%2Crating%2Copening_hours%2Cgeometry
  &input=Museum%20of%20Contemporary%20Art%20Australia
  &inputtype=textquery
  &key=YOUR_API_KEY
The following example shows a Find Place request for "Mongolian Grill", using the locationbias parameter to prefer results within 2000 meters of the specified coordinates:

URL
cURL

https://maps.googleapis.com/maps/api/place/findplacefromtext/json
  ?fields=formatted_address%2Cname%2Crating%2Copening_hours%2Cgeometry
  &input=mongolian
  &inputtype=textquery
  &locationbias=circle%3A2000%4047.6918452%2C-122.2226413
  &key=YOUR_API_KEY
The following example shows a Find Place request for a phone number. Note that the international call prefix "+" has been encoded to %2B so that this request is a compliant URL. Left unencoded, the + prefix would be decoded to a space on the server, resulting in an invalid phone number lookup.

URL
cURL

https://maps.googleapis.com/maps/api/place/findplacefromtext/json
  ?input=%2B16502530000
  &inputtype=phonenumber
  &key=YOUR_API_KEY
Find Place responses
A Find Place response contains only the data types that were specified using the fields parameter, plus html_attributions. The following example shows the response for a Find Place request for "Museum of Contemporary Art Australia", including the formatted_address, geometry, name, opening_hours, photos, rating fields.

JSON
XML

<FindPlaceFromTextResponse>
 <candidates>
  <name>Museum of Contemporary Art Australia</name>
  <formatted_address>140 George St, The Rocks NSW 2000, Australia</formatted_address>
  <geometry>
   <location>
    <lat>-33.8599358</lat>
    <lng>151.2090295</lng>
   </location>
   <viewport>
    <southwest>
     <lat>-33.8609434</lat>
     <lng>151.2077390</lng>
    </southwest>
    <northeast>
     <lat>-33.8582438</lat>
     <lng>151.2104387</lng>
    </northeast>
   </viewport>
  </geometry>
  <rating>4.4</rating>
  <opening_hours>
   <open_now>false</open_now>
  </opening_hours>
 </candidates>
 <status>OK</status>
</FindPlaceFromTextResponse>
PlacesFindPlaceFromTextResponse 
Field	Required	Type	Description
candidates
required	Array<Place>	
Contains an array of Place candidates.

Place Search requests return a subset of the fields that are returned by Place Details requests. If the field you want is not returned by Place Search, you can use Place Search to get a place_id, then use that Place ID to make a Place Details request.
See Place for more information.

status
required	PlacesSearchStatus	
Contains the status of the request, and may contain debugging information to help you track down why the request failed.

See PlacesSearchStatus for more information.

error_message
optional	string	
When the service returns a status code other than OK<, there may be an additional error_message field within the response object. This field contains more detailed information about thereasons behind the given status code. This field is not always returned, and its content is subject to change.

info_messages
optional	Array<string>	
When the service returns additional information about the request specification, there may be an additional info_messages field within the response object. This field is only returned for successful requests. It may not always be returned, and its content is subject to change.

PlacesSearchStatus
Status codes returned by service.

OK indicating the API request was successful.
ZERO_RESULTS indicating that the search was successful but returned no results. This may occur if the search was passed a latlng in a remote location.
INVALID_REQUEST indicating the API request was malformed, generally due to missing required query parameter (location or radius).
OVER_QUERY_LIMIT indicating any of the following:
You have exceeded the QPS limits.
Billing has not been enabled on your account.
The monthly $200 credit, or a self-imposed usage cap, has been exceeded.
The provided method of payment is no longer valid (for example, a credit card has expired).
See the Maps FAQ for more information about how to resolve this error.
REQUEST_DENIED indicating that your request was denied, generally because:
The request is missing an API key.
The key parameter is invalid.
UNKNOWN_ERROR indicating an unknown error.
Place
Attributes describing a place. Not all attributes will be available for all place types.

Field	Required	Type	Description
address_components
optional	Array<AddressComponent>	
An array containing the separate components applicable to this address.

See AddressComponent for more information.

adr_address
optional	string	
A representation of the place's address in the adr microformat.

business_status
optional	string	
Indicates the operational status of the place, if it is a business. If no data exists, business_status is not returned.

The allowed values include: OPERATIONAL, CLOSED_TEMPORARILY, and CLOSED_PERMANENTLY
curbside_pickup
optional	boolean	
Specifies if the business supports curbside pickup.

current_opening_hours
optional	PlaceOpeningHours	
Contains the hours of operation for the next seven days (including today). The time period starts at midnight on the date of the request and ends at 11:59 pm six days later. This field includes the special_days subfield of all hours, set for dates that have exceptional hours.

See PlaceOpeningHours for more information.

delivery
optional	boolean	
Specifies if the business supports delivery.

dine_in
optional	boolean	
Specifies if the business supports indoor or outdoor seating options.

editorial_summary
optional	PlaceEditorialSummary	
Contains a summary of the place. A summary is comprised of a textual overview, and also includes the language code for these if applicable. Summary text must be presented as-is and can not be modified or altered.

See PlaceEditorialSummary for more information.

formatted_address
optional	string	
A string containing the human-readable address of this place.

Often this address is equivalent to the postal address. Note that some countries, such as the United Kingdom, do not allow distribution of true postal addresses due to licensing restrictions.

The formatted address is logically composed of one or more address components. For example, the address "111 8th Avenue, New York, NY" consists of the following components: "111" (the street number), "8th Avenue" (the route), "New York" (the city) and "NY" (the US state).

Do not parse the formatted address programmatically. Instead you should use the individual address components, which the API response includes in addition to the formatted address field.

formatted_phone_number
optional	string	
Contains the place's phone number in its local format.

geometry
optional	Geometry	
Contains the location and viewport for the location.

See Geometry for more information.

icon
optional	string	
Contains the URL of a suggested icon which may be displayed to the user when indicating this result on a map.

icon_background_color
optional	string	
Contains the default HEX color code for the place's category.

icon_mask_base_uri
optional	string	
Contains the URL of a recommended icon, minus the .svg or .png file type extension.

international_phone_number
optional	string	
Contains the place's phone number in international format. International format includes the country code, and is prefixed with the plus, +, sign. For example, the international_phone_number for Google's Sydney, Australia office is +61 2 9374 4000.

name
optional	string	
Contains the human-readable name for the returned result. For establishment results, this is usually the canonicalized business name.

opening_hours
optional	PlaceOpeningHours	
Contains the regular hours of operation.

See PlaceOpeningHours for more information.

permanently_closed
optional	boolean	
permanently_closed is deprecated.
Use business_status to get the operational status of businesses.

photos
optional	Array<PlacePhoto>	
An array of photo objects, each containing a reference to an image. A request may return up to ten photos. More information about place photos and how you can use the images in your application can be found in the Place Photos documentation.

See PlacePhoto for more information.

place_id
optional	string	
A textual identifier that uniquely identifies a place. To retrieve information about the place, pass this identifier in the place_id field of a Places API request. For more information about place IDs, see the place ID overview.

plus_code
optional	PlusCode	
An encoded location reference, derived from latitude and longitude coordinates, that represents an area: 1/8000th of a degree by 1/8000th of a degree (about 14m x 14m at the equator) or smaller. Plus codes can be used as a replacement for street addresses in places where they do not exist (where buildings are not numbered or streets are not named). See Open Location Code and plus codes.

See PlusCode for more information.

price_level
optional	number	
The price level of the place, on a scale of 0 to 4. The exact amount indicated by a specific value will vary from region to region. Price levels are interpreted as follows:

0 Free
1 Inexpensive
2 Moderate
3 Expensive
4 Very Expensive
rating
optional	number	
Contains the place's rating, from 1.0 to 5.0, based on aggregated user reviews.

reference
optional	string	
reference is deprecated.
reservable
optional	boolean	
Specifies if the place supports reservations.

reviews
optional	Array<PlaceReview>	
A JSON array of up to five reviews. By default, the reviews are sorted in order of relevance. Use the reviews_sort request parameter to control sorting.

For most_relevant (default), reviews are sorted by relevance; the service will bias the results to return reviews originally written in the preferred language.
For newest, reviews are sorted in chronological order; the preferred language does not affect the sort order.
Google recommends indicating to users whether results are ordered by most_relevant or newest.

See PlaceReview for more information.

scope
optional	string	
scope is deprecated.
secondary_opening_hours
optional	Array<PlaceOpeningHours>	
Contains an array of entries for the next seven days including information about secondary hours of a business. Secondary hours are different from a business's main hours. For example, a restaurant can specify drive through hours or delivery hours as its secondary hours. This field populates the type subfield, which draws from a predefined list of opening hours types (such as DRIVE_THROUGH, PICKUP, or TAKEOUT) based on the types of the place. This field includes the special_days subfield of all hours, set for dates that have exceptional hours.

See PlaceOpeningHours for more information.

serves_beer
optional	boolean	
Specifies if the place serves beer.

serves_breakfast
optional	boolean	
Specifies if the place serves breakfast.

serves_brunch
optional	boolean	
Specifies if the place serves brunch.

serves_dinner
optional	boolean	
Specifies if the place serves dinner.

serves_lunch
optional	boolean	
Specifies if the place serves lunch.

serves_vegetarian_food
optional	boolean	
Specifies if the place serves vegetarian food.

serves_wine
optional	boolean	
Specifies if the place serves wine.

takeout
optional	boolean	
Specifies if the business supports takeout.

types
optional	Array<string>	
Contains an array of feature types describing the given result. See the list of supported types.

url
optional	string	
Contains the URL of the official Google page for this place. This will be the Google-owned page that contains the best available information about the place. Applications must link to or embed this page on any screen that shows detailed results about the place to the user.

user_ratings_total
optional	number	
The total number of reviews, with or without text, for this place.

utc_offset
optional	number	
Contains the number of minutes this place’s current timezone is offset from UTC. For example, for places in Sydney, Australia during daylight saving time this would be 660 (+11 hours from UTC), and for places in California outside of daylight saving time this would be -480 (-8 hours from UTC).

vicinity
optional	string	
For establishment (types:["establishment", ...]) results only, the vicinity field contains a simplified address for the place, including the street name, street number, and locality, but not the province/state, postal code, or country.

For all other results, the vicinity field contains the name of the narrowest political (types:["political", ...]) feature that is present in the address of the result.

This content is meant to be read as-is. Do not programmatically parse the formatted address.

website
optional	string	
The authoritative website for this place, such as a business' homepage.

wheelchair_accessible_entrance
optional	boolean	
Specifies if the place has an entrance that is wheelchair-accessible.

AddressComponent
Field	Required	Type	Description
long_name
required	string	
The full text description or name of the address component as returned by the Geocoder.

short_name
required	string	
An abbreviated textual name for the address component, if available. For example, an address component for the state of Alaska may have a long_name of "Alaska" and a short_name of "AK" using the 2-letter postal abbreviation.

types
required	Array<string>	
An array indicating the type of the address component. See the list of supported types.

PlaceEditorialSummary
Contains a summary of the place. A summary is comprised of a textual overview, and also includes the language code for these if applicable. Summary text must be presented as-is and can not be modified or altered.

Field	Required	Type	Description
language
optional	string	
The language of the previous fields. May not always be present.

overview
optional	string	
A medium-length textual summary of the place.

Geometry
An object describing the location.

Field	Required	Type	Description
location
required	LatLngLiteral	See LatLngLiteral for more information.
viewport
required	Bounds	See Bounds for more information.
LatLngLiteral
An object describing a specific location with Latitude and Longitude in decimal degrees.

Field	Required	Type	Description
lat
required	number	
Latitude in decimal degrees

lng
required	number	
Longitude in decimal degrees

Bounds
A rectangle in geographical coordinates from points at the southwest and northeast corners.

Field	Required	Type	Description
northeast
required	LatLngLiteral	See LatLngLiteral for more information.
southwest
required	LatLngLiteral	See LatLngLiteral for more information.
PlaceOpeningHours
An object describing the opening hours of a place.

Field	Required	Type	Description
open_now
optional	boolean	
A boolean value indicating if the place is open at the current time.

periods
optional	Array<PlaceOpeningHoursPeriod>	
An array of opening periods covering seven days, starting from Sunday, in chronological order.

See PlaceOpeningHoursPeriod for more information.

special_days
optional	Array<PlaceSpecialDay>	
An array of up to seven entries corresponding to the next seven days.

See PlaceSpecialDay for more information.

type
optional	string	
A type string used to identify the type of secondary hours (for example, DRIVE_THROUGH, HAPPY_HOUR, DELIVERY, TAKEOUT, KITCHEN, BREAKFAST, LUNCH, DINNER, BRUNCH, PICKUP, SENIOR_HOURS). Set for secondary_opening_hours only.

weekday_text
optional	Array<string>	
An array of strings describing in human-readable text the hours of the place.

PlaceOpeningHoursPeriod 
Field	Required	Type	Description
open
required	PlaceOpeningHoursPeriodDetail	
Contains a pair of day and time objects describing when the place opens.

See PlaceOpeningHoursPeriodDetail for more information.

close
optional	PlaceOpeningHoursPeriodDetail	
May contain a pair of day and time objects describing when the place closes. If a place is always open, the close section will be missing from the response. Clients can rely on always-open being represented as an open period containing day with value 0 and time with value 0000, and no close.

See PlaceOpeningHoursPeriodDetail for more information.

PlaceSpecialDay
Field	Required	Type	Description
date
optional	string	
A date expressed in RFC3339 format in the local timezone for the place, for example 2010-12-31.

exceptional_hours
optional	boolean	
True if there are exceptional hours for this day. If true, this means that there is at least one exception for this day. Exceptions cause different values to occur in the subfields of current_opening_hours and secondary_opening_hours such as periods, weekday_text, open_now. The exceptions apply to the hours, and the hours are used to generate the other fields.

PlaceOpeningHoursPeriodDetail 
Field	Required	Type	Description
day
required	number	
A number from 0–6, corresponding to the days of the week, starting on Sunday. For example, 2 means Tuesday.

time
required	string	
May contain a time of day in 24-hour hhmm format. Values are in the range 0000–2359. The time will be reported in the place’s time zone.

date
optional	string	
A date expressed in RFC3339 format in the local timezone for the place, for example 2010-12-31.

truncated
optional	boolean	
True if a given period was truncated due to a seven-day cutoff, where the period starts before midnight on the date of the request and/or ends at or after midnight on the last day. This property indicates that the period for open or close can extend past this seven-day cutoff.

PlacePhoto
A photo of a Place. The photo can be accesed via the Place Photo API using an url in the following pattern:


https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=photo_reference&key=YOUR_API_KEY
See Place Photos for more information.

Field	Required	Type	Description
height
required	number	
The height of the photo.

html_attributions
required	Array<string>	
The HTML attributions for the photo.

photo_reference
required	string	
A string used to identify the photo when you perform a Photo request.

width
required	number	
The width of the photo.

PlusCode
An encoded location reference, derived from latitude and longitude coordinates, that represents an area, 1/8000th of a degree by 1/8000th of a degree (about 14m x 14m at the equator) or smaller. Plus codes can be used as a replacement for street addresses in places where they do not exist (where buildings are not numbered or streets are not named).

Field	Required	Type	Description
global_code
required	string	
The global_code is a 4 character area code and 6 character or longer local code (849VCWC8+R9).

compound_code
optional	string	
The compound_code is a 6 character or longer local code with an explicit location (CWC8+R9, Mountain View, CA, USA). Some APIs may return an empty string if the compound_code is not available.

PlaceReview
A review of the place submitted by a user.

Field	Required	Type	Description
author_name
required	string	
The name of the user who submitted the review. Anonymous reviews are attributed to "A Google user".

rating
required	number	
The user's overall rating for this place. This is a whole number, ranging from 1 to 5.

relative_time_description
required	string	
The time that the review was submitted in text, relative to the current time.

time
required	number	
The time that the review was submitted, measured in the number of seconds since since midnight, January 1, 1970 UTC.

author_url
optional	string	
The URL to the user's Google Maps Local Guides profile, if available.

language
optional	string	
An IETF language code indicating the language of the returned review.This field contains the main language tag only, and not the secondary tag indicating country or region. For example, all the English reviews are tagged as 'en', and not 'en-AU' or 'en-UK' and so on.This field is empty if there is only a rating with no review text.

original_language
optional	string	
An IETF language code indicating the original language of the review. If the review has been translated, then original_language != language.This field contains the main language tag only, and not the secondary tag indicating country or region. For example, all the English reviews are tagged as 'en', and not 'en-AU' or 'en-UK' and so on.This field is empty if there is only a rating with no review text.

profile_photo_url
optional	string	
The URL to the user's profile photo, if available.

text
optional	string	
The user's review. When reviewing a location with Google Places, text reviews are considered optional. Therefore, this field may be empty. Note that this field may include simple HTML markup. For example, the entity reference &amp; may represent an ampersand character.

translated
optional	boolean	
A boolean value indicating if the review was translated from the original language it was written in.If a review has been translated, corresponding to a value of true, Google recommends that you indicate this to your users. For example, you can add the following string, “Translated by Google”, to the review.