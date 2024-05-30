#include <pistache/endpoint.h>
#include <pistache/http.h>
#include <pistache/router.h>
#include <iostream>
#include <fstream>
#include <opencv2/opencv.hpp>
#include <nlohmann/json.hpp>
#include <filesystem>

using namespace Pistache;
using json = nlohmann::json;

const std::string image_dir = "/home/aahil/edhithaGCS/src/assets/DispImages";

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

        // Route to handle preflight requests
        Routes::Options(router, "/crop-image-preview", Routes::bind(&ImageHandler::handleOptions, this));

        // Route to list all images
        Routes::Get(router, "/all-images", Routes::bind(&ImageHandler::listAllImages, this));

        // Route to serve individual images
        Routes::Get(router, "/images/:filename", Routes::bind(&ImageHandler::serveImage, this));

        // Route to handle image cropping preview
        Routes::Post(router, "/crop-image-preview", Routes::bind(&ImageHandler::cropImagePreview, this));
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
        response.headers().add<Http::Header::AccessControlAllowOrigin>("*");
        response.headers().add<Http::Header::AccessControlAllowMethods>("GET");
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
        response.headers().add<Http::Header::AccessControlAllowOrigin>("*");
        response.headers().add<Http::Header::AccessControlAllowMethods>("GET");

        std::stringstream buffer;
        buffer << image_file.rdbuf();
        response.send(Http::Code::Ok, buffer.str());
    }

    void cropImagePreview(const Rest::Request &request, Http::ResponseWriter response)
    {
        auto data = json::parse(request.body());
        std::string imageUrl = data["imageUrl"];
        int clickX = data["clickX"];
        int clickY = data["clickY"];

        std::string imagePath = image_dir + "/" + imageUrl;

        cv::Mat image = cv::imread(imagePath, cv::IMREAD_UNCHANGED);
        if (image.empty())
        {
            response.send(Http::Code::Internal_Server_Error, "Failed to open image");
            return;
        }

        int cropWidth = 200;
        int cropHeight = 200;
        int startX = std::max(0, clickX - cropWidth / 2);
        int startY = std::max(0, clickY - cropHeight / 2);
        int endX = std::min(image.cols, startX + cropWidth);
        int endY = std::min(image.rows, startY + cropHeight);

        cv::Rect cropRegion(startX, startY, endX - startX, endY - startY);
        cv::Mat croppedImage = image(cropRegion);

        std::vector<uchar> buffer;
        cv::imencode(".png", croppedImage, buffer); // Encode cropped image to PNG format

        response.headers().add<Http::Header::ContentType>("image/png");
        response.headers().add<Http::Header::AccessControlAllowOrigin>("*");
        response.send(Http::Code::Ok, reinterpret_cast<const char *>(buffer.data()), Http::Mime::MediaType::fromString("image/png"));
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
