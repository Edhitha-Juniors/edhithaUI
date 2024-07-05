#include <pistache/endpoint.h>
#include <pistache/http.h>
#include <pistache/router.h>
#include <iostream>
#include <fstream>
#include <opencv2/opencv.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <nlohmann/json.hpp>
#include <filesystem>

using namespace Pistache;
using json = nlohmann::json;

const std::string image_dir = "/Users/aahil/Downloads/edhithaGCS/src/assets/DispImages";
const std::string cropped_image_dir = "/Users/aahil/Downloads/edhithaGCS/src/assets/CroppedImages";

class ImageHandler
{
public:
    ImageHandler(Address addr) : httpEndpoint(std::make_shared<Http::Endpoint>(addr)) {}

    void init(size_t threads = 1)
    {
        auto opts = Http::Endpoint::options().threads(static_cast<int>(threads));
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

    void handleOptions(const Rest::Request &, Http::ResponseWriter response)
    {
        response.headers().add<Http::Header::AccessControlAllowOrigin>("*");
        response.headers().add<Http::Header::AccessControlAllowMethods>("GET, POST, OPTIONS");
        response.headers().add<Http::Header::AccessControlAllowHeaders>("Content-Type");
        response.send(Http::Code::Ok);
    }

private:
    void setupRoutes()
    {
        using namespace Rest;

        Routes::Options(router, "/crop-image", Routes::bind(&ImageHandler::handleOptions, this));

        // Route to list all images
        Routes::Get(router, "/all-images", Routes::bind(&ImageHandler::listAllImages, this));

        // Route to serve individual images
        Routes::Get(router, "/images/:filename", Routes::bind(&ImageHandler::serveImage, this));

        // Route to handle image cropping
        Routes::Post(router, "/crop-image", Routes::bind(&ImageHandler::cropImage, this));
    }

    void addCorsHeaders(Http::ResponseWriter &response)
    {
        response.headers().add<Http::Header::AccessControlAllowOrigin>("*");
        response.headers().add<Http::Header::AccessControlAllowMethods>("GET, POST, OPTIONS");
        response.headers().add<Http::Header::AccessControlAllowHeaders>("Content-Type");
    }

    void listAllImages(const Rest::Request &request, Http::ResponseWriter response)
    {
        std::vector<std::string> imageUrls;
        for (const auto &entry : std::filesystem::directory_iterator(image_dir))
        {
            if (entry.is_regular_file())
            {
                imageUrls.push_back(entry.path().filename().string());
            }
        }
        json responseJson = {{"imageUrls", imageUrls}};
        response.headers().add<Http::Header::ContentType>("application/json");
        addCorsHeaders(response);
        response.send(Http::Code::Ok, responseJson.dump());
    }

    void serveImage(const Rest::Request &request, Http::ResponseWriter response)
    {
        auto filename = request.param(":filename").as<std::string>();
        std::string image_path = image_dir + "/" + filename;

        if (!std::filesystem::exists(image_path))
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
        addCorsHeaders(response);

        std::stringstream buffer;
        buffer << image_file.rdbuf();
        response.send(Http::Code::Ok, buffer.str());
    }

    void cropImage(const Rest::Request &request, Http::ResponseWriter response)
    {
        try
        {
            auto body = request.body();
            auto jsonBody = json::parse(body);

            if (jsonBody.contains("imageUrl") && jsonBody.contains("coordinates"))
            {
                std::string imageUrl = jsonBody["imageUrl"];
                std::string coordinates = jsonBody["coordinates"];

                std::cout << "Received image URL: " << imageUrl << std::endl;
                std::cout << "Received coordinates: " << coordinates << std::endl;

                // Parse coordinates
                int x, y;
                sscanf(coordinates.c_str(), "%d,%d", &x, &y);

                // Load the image using OpenCV
                std::string image_path = image_dir + "/" + std::filesystem::path(imageUrl).filename().string();
                cv::Mat image = cv::imread(image_path);
                if (image.empty())
                {
                    response.send(Http::Code::Internal_Server_Error, "Failed to load image");
                    return;
                }

                // Calculate crop rectangle
                int crop_size = 200;
                int half_crop_size = crop_size / 2;
                int x_start = std::max(0, x - half_crop_size);
                int y_start = std::max(0, y - half_crop_size);
                int x_end = std::min(image.cols, x + half_crop_size);
                int y_end = std::min(image.rows, y + half_crop_size);

                cv::Rect crop_rect(x_start, y_start, x_end - x_start, y_end - y_start);

                // Crop the image
                cv::Mat cropped_image = image(crop_rect);

                // Save the cropped image
                std::string cropped_image_filename = "cropped_" + std::filesystem::path(imageUrl).filename().string();
                std::string cropped_image_path = cropped_image_dir + "/" + cropped_image_filename;
                cv::imwrite(cropped_image_path, cropped_image);

                json responseJson = {{"status", "success"}, {"message", "Image cropped successfully"}, {"croppedImageUrl", "/images/" + cropped_image_filename}};
                response.headers().add<Http::Header::ContentType>("application/json");
                addCorsHeaders(response);
                response.send(Http::Code::Ok, responseJson.dump());
            }
            else
            {
                response.send(Http::Code::Bad_Request, "Invalid request payload");
            }
        }
        catch (const std::exception &e)
        {
            response.send(Http::Code::Internal_Server_Error, "An error occurred");
        }
    }

    std::shared_ptr<Http::Endpoint> httpEndpoint;
    Rest::Router router;
};

int main()
{
    Address addr(Ipv4::any(), Port(9080));
    ImageHandler imageHandler(addr);

    imageHandler.init();
    imageHandler.start();
    imageHandler.shutdown();

    return 0;
}
