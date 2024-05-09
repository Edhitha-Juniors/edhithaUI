#include <crow.h>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <nlohmann/json.hpp> // Include nlohmann/json library
#include <chrono>
#include <thread>

using json = nlohmann::json; // Alias for nlohmann::json

namespace fs = std::filesystem;

// Function to fetch image list from the directory
json getImageList()
{
    std::vector<std::string> imageList;
    for (const auto &entry : fs::directory_iterator("../../src/assets/images/"))
    {
        imageList.push_back(entry.path().filename().string());
    }
    return json(imageList);
}

int main()
{
    crow::SimpleApp app;

    // Route to serve individual images
    CROW_ROUTE(app, "/img/<string>")
    ([](const crow::request &req, crow::response &res, std::string filename)
     {
        std::string imagePath = "../../src/assets/images/" + filename;
        std::ifstream file(imagePath, std::ios::binary);
        if (!file) {
            res.code = 404;
            res.write("Image NF");
            res.end();
            return;
        }
        std::ostringstream oss;
        oss << file.rdbuf();
        res.set_header("Access-Control-Allow-Origin", "*");
        res.set_header("Access-Control-Allow-Methods", "GET, OPTIONS");
        res.set_header("Access-Control-Allow-Headers", "Content-Type");
        res.set_header("Content-Type", "image/jpeg");
        res.write(oss.str());
        res.end(); });

    // Route to serve image list
    CROW_ROUTE(app, "/imglst")
    ([]()
     {
        // Get the initial image list
        json initialList = getImageList();
        
        // Create a response with initial image list
        crow::response res(initialList.dump());
        
        // Set CORS headers to allow requests from all origins
        res.set_header("Access-Control-Allow-Origin", "*");
        res.set_header("Access-Control-Allow-Methods", "GET, OPTIONS");
        res.set_header("Access-Control-Allow-Headers", "Content-Type");
        
        return res; });

    // Function to periodically fetch and update the image list
    auto updateImageList = [&app]()
    {
        while (true)
        {
            // Fetch the latest image list
            json latestList = getImageList();

            // Broadcast the updated image list to all clients
            app.get_context<crow::app>()->broadcast("/imglst", latestList.dump());

            // Sleep for 5 seconds before fetching again
            std::this_thread::sleep_for(std::chrono::seconds(5));
        }
    };

    // Start the thread to periodically update the image list
    std::thread(updateImageList).detach();

    // Run the server
    app.bindaddr("127.0.0.1").port(8080).multithreaded().run();

    return 0;
}
