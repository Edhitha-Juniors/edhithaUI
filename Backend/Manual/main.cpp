#include <pistache/endpoint.h>
#include <pistache/http.h>
#include <pistache/router.h>
#include <fstream>
#include <filesystem>
#include <string>
#include <sstream>
#include <chrono>
#include <thread>
#include <nlohmann/json.hpp> // Include the JSON library
#include <algorithm>         // Include the algorithm library for sorting

const std::string image_dir = "/home/aahil/edhithaGCS/src/assets/images"; // Replace with your actual directory
using namespace Pistache;
using namespace std::filesystem;
using json = nlohmann::json;

class ImageHandler
{
public:
    ImageHandler(Address addr)
        : httpEndpoint(std::make_shared<Http::Endpoint>(addr)) {}

    void init(size_t threads = 1)
    {
        auto opts = Http::Endpoint::options()
                        .threads(static_cast<int>(threads));
        httpEndpoint->init(opts);
        setupRoutes();
    }

    void start()
    {
        httpEndpoint->setHandler(router.handler());
        httpEndpoint->serve();
    }

    void shutdown()
    {
        httpEndpoint->shutdown();
    }

private:
    void setupRoutes()
    {
        using namespace Rest;

        Routes::Get(router, "/all-images", Routes::bind(&ImageHandler::listAllImages, this));
        Routes::Get(router, "/images/:filename", Routes::bind(&ImageHandler::serveImage, this));
        Routes::Post(router, "/toggle-connection", Routes::bind(&ImageHandler::toggleConnection, this));
        Routes::Post(router, "/toggle-geotag", Routes::bind(&ImageHandler::toggleGeotag, this));
        Routes::Post(router, "/lock-servo", Routes::bind(&ImageHandler::lockServo, this));
        Routes::Post(router, "/mission-start", Routes::bind(&ImageHandler::missionStart, this));
        Routes::Post(router, "/arm-drone", Routes::bind(&ImageHandler::armDrone, this));
        Routes::Post(router, "/disarm-drone", Routes::bind(&ImageHandler::disarmDrone, this));
        Routes::Post(router, "/guided", Routes::bind(&ImageHandler::guided, this));
        Routes::Post(router, "/auto", Routes::bind(&ImageHandler::autoMode, this));
        Routes::Post(router, "/rtl", Routes::bind(&ImageHandler::rtl, this));
    }

    void listAllImages(const Rest::Request &request, Http::ResponseWriter response)
    {
        std::vector<std::string> imageUrls;
        for (const auto &entry : directory_iterator(image_dir))
        {
            if (entry.is_regular_file())
            {
                imageUrls.push_back(entry.path().filename().string());
            }
        }

        // Sort the image URLs to ensure new images are added at the end
        std::sort(imageUrls.begin(), imageUrls.end());

        json responseJson = {{"imageUrls", imageUrls}};
        response.headers().add<Http::Header::ContentType>("application/json");
        response.headers().add<Http::Header::AccessControlAllowOrigin>("*"); // Add CORS header
        response.send(Http::Code::Ok, responseJson.dump());
    }

    void serveImage(const Rest::Request &request, Http::ResponseWriter response)
    {
        auto filename = request.param(":filename").as<std::string>();
        std::string image_path = image_dir + "/" + filename;

        if (!exists(image_path))
        {
            response.send(Http::Code::Not_Found, "Image not found");
            return;
        }

        std::ifstream image_file(image_path, std::ios::binary);
        if (!image_file.is_open())
        {
            response.send(Http::Code::Internal_Server_Error, "Failed to open image");
            return;
        }

        image_file.seekg(0, std::ios::end);
        size_t image_size = image_file.tellg();
        image_file.seekg(0, std::ios::beg);

        std::string content_type = "image/";
        if (filename.find(".jpg") != std::string::npos)
        {
            content_type += "jpeg";
        }
        else if (filename.find(".png") != std::string::npos)
        {
            content_type += "png";
        }
        else
        {
            response.send(Http::Code::Bad_Request, "Unsupported image format");
            return;
        }

        response.headers().add<Http::Header::ContentType>(content_type);
        response.headers().add<Http::Header::ContentLength>(image_size);
        response.headers().add<Http::Header::AccessControlAllowOrigin>("*"); // Add CORS header
        response.headers().add<Http::Header::AccessControlAllowMethods>("GET");

        std::stringstream buffer;
        buffer << image_file.rdbuf();
        response.send(Http::Code::Ok, buffer.str());
    }

    void toggleConnection(const Rest::Request &request, Http::ResponseWriter response)
    {
        // Logic for toggling connection
        std::cout << "Toggle Connection button pressed" << std::endl;
        response.send(Http::Code::Ok, "Connection toggled");
    }

    void toggleGeotag(const Rest::Request &request, Http::ResponseWriter response)
    {
        // Logic for toggling geotag
        std::cout << "Toggle Geotag button pressed" << std::endl;
        response.send(Http::Code::Ok, "Geotag toggled");
    }

    void lockServo(const Rest::Request &request, Http::ResponseWriter response)
    {
        // Logic for locking servo
        std::cout << "Lock Servo button pressed" << std::endl;
        response.send(Http::Code::Ok, "Servo locked");
    }

    void missionStart(const Rest::Request &request, Http::ResponseWriter response)
    {
        // Logic for starting mission
        std::cout << "Mission Start button pressed" << std::endl;
        response.send(Http::Code::Ok, "Mission started");
    }

    void armDrone(const Rest::Request &request, Http::ResponseWriter response)
    {
        // Logic for arming drone
        std::cout << "Arm Drone button pressed" << std::endl;
        response.send(Http::Code::Ok, "Drone armed");
    }

    void disarmDrone(const Rest::Request &request, Http::ResponseWriter response)
    {
        // Logic for disarming drone
        std::cout << "Disarm Drone button pressed" << std::endl;
        response.send(Http::Code::Ok, "Drone disarmed");
    }

    void guided(const Rest::Request &request, Http::ResponseWriter response)
    {
        // Logic for setting guided mode
        std::cout << "Guided button pressed" << std::endl;
        response.send(Http::Code::Ok, "Drone set to guided mode");
    }

    void autoMode(const Rest::Request &request, Http::ResponseWriter response)
    {
        // Logic for setting auto mode
        std::cout << "Auto button pressed" << std::endl;
        response.send(Http::Code::Ok, "Drone set to auto mode");
    }

    void rtl(const Rest::Request &request, Http::ResponseWriter response)
    {
        // Logic for return-to-launch
        std::cout << "RTL button pressed" << std::endl;
        response.send(Http::Code::Ok, "Drone set to return-to-launch mode");
    }

    std::shared_ptr<Http::Endpoint> httpEndpoint;
    Rest::Router router;
};

void checkForNewImages()
{
    while (true)
    {
        // Check for new images in the directory
        // Your logic to check for new images here

        // Sleep for 2 seconds
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }
}

int main()
{
    std::thread imageCheckThread(checkForNewImages);

    Pistache::Address addr(Pistache::Ipv4::any(), Pistache::Port(9080));
    ImageHandler handler(addr);

    handler.init(1);
    handler.start();

    imageCheckThread.join();

    handler.shutdown();

    return 0;
}
