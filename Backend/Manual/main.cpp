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
    CROW_ROUTE(app, "/")
    ([]()
     {
         std::string imagePath = "/home/aahil/edhithaGCS/src/assets/images/imagename.jpg";
         std::string imageContent = readImageFile(imagePath);
         if (imageContent.empty())
         {
             return crow::response("L");
         }
         return crow::response(200, imageContent); // Return image content
     });

    app.bindaddr("127.0.0.1").port(8080).multithreaded().run();

    return 0;
}
