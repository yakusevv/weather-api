a small microservice that stores the temperature of one city every hour (data is loaded from https://openweathermap.org/api)
it returns the temperature history (metric) for the day in format 
{
    data: {
        "00:00": 10,
        "01:00": 9.6
        --||--
    }
}
params:
  - day – required GET parameter in Y-m-d format;
  - x-token - a line of 32 characters is transmitted through the header;
