#include <crow.h>
#include <fstream>
#include <sstream>

// Function to read an image file into a string
std::string readImageFile(const std::string &filePath)
{
    std::ifstream file(filePath, std::ios::binary);
    if (!file)
    {
        return ""; // Return empty string if file cannot be opened
    }

    std::ostringstream oss;
    oss << file.rdbuf();
    return oss.str();
}

int main()
{
    crow::SimpleApp app;

    // Route to handle image requests
    CROW_ROUTE(app, "/img")
    ([]()
     {
         std::string imagePath = "../../src/assets/images/image2.jpg";
         std::string imageContent = readImageFile(imagePath);
         if (imageContent.empty())
         {
             return crow::response("L");
         }
         // Create a response with the image content
         crow::response res(imageContent);
         
         // Set CORS headers to allow requests from all origins
         res.add_header("Access-Control-Allow-Origin", "*");
         res.add_header("Access-Control-Allow-Methods", "GET, OPTIONS");
         res.add_header("Access-Control-Allow-Headers", "Content-Type");
         
         return res; });

    app.bindaddr("127.0.0.1").port(8080).multithreaded().run();

    return 0;
}
