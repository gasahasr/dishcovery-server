Make a request
REST, or Representational State Transfer, in the Custom Search JSON API is somewhat different from the usual RESTful APIs. Instead of providing access to resources, the API provides access to a service. As a result, the API provides a single URI that acts as the service endpoint.

You can retrieve results for a particular search by sending an HTTP GET request to its URI. You pass in the details of the search request as query parameters. The format for the Custom Search JSON API URI is:


https://www.googleapis.com/customsearch/v1?[parameters]
Three query [parameters] are required with each search request:

API key - Use the key query parameter to identify your application.

Programmable Search Engine ID - Use cx to specify the Programmable Search Engine you want to use to perform this search. The search engine must be created with the Control Panel Note: The Search Engine ID (cx) can be of different format (e.g. 8ac1ab64606d234f1)
Search query - Use the q query parameter to specify your search expression.

All other query parameters are optional.

Here is an example of a request which searches a test Programmable Search Engine for lectures:


GET https://www.googleapis.com/customsearch/v1?key=INSERT_YOUR_API_KEY&cx=017576662512468239146:omuauf_lfve&q=lectures
Note: The limit on the length of the search request should be within 2048 characters.
Query parameters
There are two types of parameters that you can pass in your request:

API-specific parameters - define properties of your search, like the search expression, number of results, language etc.
Standard query parameters - define technical aspects of your request, like the API key.
All parameter values need to be URL encoded.

API-specific query parameters
Request parameters that apply specifically to the Custom Search JSON API and define your search request are summarized in the reference.

Standard query parameters
Query parameters that apply to all Custom Search JSON API operations are documented at System Parameters.

Response data
If the request succeeds, the server responds with a 200 OK HTTP status code and the response data in JSON format. You can look up the response data structure in the reference.

The response data is a JSON object that includes three types of properties:

Metadata describing the requested search (and, possibly, related search requests)
Metadata describing the Programmable Search Engine
Search results
For a detailed description of each property, see the reference.

Search request metadata
The search metadata includes:

url property, which has information about the OpenSearch template used for the results returned in this request.
queries property, which is an array of objects describing the characteristics of possible searches. The name of each object in the array is either the name of an OpenSearch query role or one of the two custom roles defined by this API: previousPage and nextPage. Possible query role objects include:
request: Metadata describing the query for the current set of results.
This role is always present in the response.
It is always an array with just one element.
nextPage: Metadata describing the query to use for the next page of results.
This role is not present if the current results are the last page. Note: This API returns up to the first 100 results only.
When present, it is always a array with just one element.
previousPage: Metadata describing the query to use for the previous page of results.
Not present if the current results are the first page.
When present, it is always a array with just one element.
Search engine metadata
The context property has metadata describing the search engine that performed the search query. It includes the name of the search engine, and any facet objects it provides for refining a search.

Search results
The items array contains the actual search results. The search results include the URL, title and text snippets that describe the result. In addition, they can contain rich snippet information, if applicable.

If the search results include a promotions property, it contains a set of promotions.

REST from JavaScript
You can invoke the Custom Search JSON API using REST from JavaScript, using the callback query parameter and a callback function. This lets you write rich applications that display Programmable Search Engine data without writing any server side code.

The following example uses this approach to display the first page of search results for the query lecture:


<html>
<head>
<title>Custom Search JSON API Example</title>
</head>
<body>
    <div id="content"></div>
    <p id="demo"></p>
    <script>
    function hndlr(response) {
      if (response.items == null) {
        document.getElementById("demo").innerHTML +=`<h3> No Results Found </h3>`;
      } else {
        for (var i = 1; i < response.items.length; i++) {
          var item = response.items[i];
          // Make sure HTML in item.htmlTitle is escaped.
          document.getElementById("content").append(
            document.createElement("br"),
            document.createTextNode(item.htmlTitle)
          );
        }
      }
    }
    </script>
    <script src="https://www.googleapis.com/customsearch/v1?key=YOUR-KEY&cx=017576662512468239146:omuauf_lfve&q=lecture&callback=hndlr">
    </script>
  </body>
</html>