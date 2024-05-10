#include <pistache/endpoint.h>
#include <pistache/http.h>
#include <fstream>
#include <filesystem>
#include <string>
#include <sstream>

const std::string image_dir = "/home/aahil/edhithaGCS/src/assets/images"; // Replace with your actual directory
using namespace Pistache;
using namespace std::filesystem;

class ImageHandler : public Http::Handler
{
public:
    HTTP_PROTOTYPE(ImageHandler)

    void onRequest(const Http::Request &request, Http::ResponseWriter response) override
    {
        // Extract requested image name from the URL path
        std::string path = request.resource();

        std::string image_name = path.substr(path.rfind("/") + 1);

        // Check if requested image exists
        std::string image_path = image_dir + "/" + image_name;
        if (!exists(image_path))
        {
            response.send(Http::Code::Not_Found, "Image not found");
            return;
        }

        // Read image data from file
        std::ifstream image_file(image_path, std::ios::binary);
        if (!image_file.is_open())
        {
            response.send(Http::Code::Internal_Server_Error, "Failed to open image");
            return;
        }

        // Get image size and set content type header
        image_file.seekg(0, std::ios::end);
        size_t image_size = image_file.tellg();
        image_file.seekg(0, std::ios::beg);
        std::string content_type = "image/";
        if (path.find(".jpg") != std::string::npos)
        {
            content_type += "jpeg";
        }
        else if (path.find(".png") != std::string::npos)
        {
            content_type += "png";
        }
        else
        {
            response.send(Http::Code::Bad_Request, "Unsupported image format");
            return;
        }
        response.headers().add<Pistache::Http::Header::ContentType>(content_type);

        // Convert image size to string and then to uint64_t for content length
        std::string content_length_str = std::to_string(image_size);
        uint64_t content_length = std::stoull(content_length_str);
        response.headers().add<Pistache::Http::Header::ContentLength>(content_length);

        // Send image data as response body
        std::stringstream buffer;
        buffer << image_file.rdbuf();
        response.send(Http::Code::Ok, buffer.str());
    }
};

int main()
{
    Pistache::Address addr(Pistache::Ipv4::any(), Pistache::Port(9080));
    auto opts = Pistache::Http::Endpoint::options()
                    .threads(1);

    Http::Endpoint server(addr);
    server.init(opts);
    server.setHandler(Http::make_handler<ImageHandler>());
    server.serve();
    return 0;
}
