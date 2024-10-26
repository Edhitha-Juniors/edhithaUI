import React from 'react';

const TransportForm = () => {
  const DottedLine = ({ width = "w-24", className = "" }) => (
    <span className={`inline-block border-b border-dotted border-black ${width} mx-1 ${className}`}></span>
  );

  return (
    <div className="max-w-4xl mx-auto p-4 bg-white text-sm">
      {/* Header */}
      <div className="text-center relative mb-4">
        <h1 className="text-sm font-normal">ಕರ್ನಾಟಕ ಸರ್ಕಾರ</h1>
        <div className="flex justify-between items-center mt-1">
          <span className="text-sm">BNG-2022</span>
          <h2 className="text-xl font-bold">ಸಾರಿಗೆ ಇಲಾಖೆ</h2>
          <div className="flex flex-col items-end">
            <span className="text-sm">ಸಂಖ್ಯೆ</span>
            <span className="text-sm">ಮೂಲಪ್ರತಿ</span>
            <DottedLine width="w-16" />
          </div>
        </div>
        <div className="text-center mt-1">
          <span className="text-sm font-normal">ತನಿಖಾ ವರದಿ ಮೂಲಪ್ರತಿ</span>
        </div>
      </div>

      {/* Rest of the form content remains the same */}
      <div className="space-y-2 text-xs">
        <div className="flex flex-wrap gap-x-4">
          <span>ಸ್ಥಳ <DottedLine /></span>
          <span>ದಿನಾಂಕ <DottedLine /></span>
          <span>ಸಮಯ <DottedLine /></span>
        </div>

        <div>
          ವಾಹನದ ನೋಂದಣಿ ಸಂಖ್ಯೆ <DottedLine width="w-32" />
          ತರಹ <DottedLine />
        </div>

        <div>
          ವಾಹನ ಮಾಲೀಕರ ಹೆಸರು ಮತ್ತು ವಿಳಾಸ <DottedLine width="w-64" />
        </div>

        <div className="w-full">
          <DottedLine width="w-full" />
        </div>

        <div>
          ವಾಹನ ಚಾಲಕನ ಹೆಸರು <DottedLine width="w-64" />
        </div>

        <div className="flex flex-wrap gap-x-4">
          <span>ಅನುಜ್ಞಾ ಪರವಾನಗಿ ಸಂಖ್ಯೆ <DottedLine /></span>
          <span>ಚಾಲನೆ ಅವಧಿ <DottedLine /></span>
        </div>

        <div className="flex flex-wrap gap-x-4">
          <span>ಮಾರ್ಗ ಸಂಖ್ಯೆ <DottedLine /></span>
          <span>ವಾಹಕನ ಹೆಸರು <DottedLine width="w-32" /></span>
        </div>

        <div className="flex flex-wrap gap-x-4">
          <span>ವಾಹಕನ ಪರವಾನಗಿಯ ಸಂಖ್ಯೆ <DottedLine /></span>
          <span>ಚಾಲನೆ ಅವಧಿ <DottedLine /></span>
        </div>

        <div className="flex flex-wrap gap-x-4">
          <span>ಮಾರ್ಗ ಸಂಖ್ಯೆ <DottedLine /></span>
          <span>ಫಿಟ್ನೆಸ್ ಅವಧಿ <DottedLine /></span>
        </div>

        <div className="flex flex-wrap gap-x-4">
          <span>ವಿಮೆಯ ಚಾಲನೆ ಅವಧಿ <DottedLine /></span>
          <span>ಪರ್ಮಿಟ್ ಮಾನ್ಯ ಸಂಖ್ಯೆ <DottedLine /></span>
        </div>

        <div className="flex flex-wrap gap-x-4">
          <span>ಚಾಲನೆ ಅವಧಿ <DottedLine /></span>
          <span>ನೋಂದಣಿ ಪುಸ್ತಕದಂತೆ ಆರ್.ಎಲ್.ಡಬ್ಲ್ಯೂ <DottedLine /></span>
        </div>

        <div className="flex flex-wrap gap-x-4">
          <span>ಎಂಜಿನ್ ನಂಬರ್ <DottedLine /></span>
          <span>ಟಯರ್ ಅಳತೆ <DottedLine /></span>
        </div>

        <div>
          ಚಾಸಿಸ್ ನಂಬರ್ <DottedLine width="w-96" />
        </div>

        <div>
          ಪರವಾನಗಿ ಸಂಖ್ಯೆ <DottedLine />
          ಚಾಲನೆ ಅವಧಿ ಮತ್ತು ಮಾರ್ಗ <DottedLine width="w-32" />
        </div>

        <div>
          ಸರಕು ವಿವರ <DottedLine width="w-96" />
        </div>

        <div>
          ವಾಹನ ಮಾರ್ಗದಲ್ಲಿ ಪತ್ತೆ ಹಾಕಿದ್ದು/ನಿಂತಿರುವಾಗ <DottedLine width="w-64" />
        </div>

        <div className="flex flex-wrap gap-x-4">
          <span>ಎಲ್ಲಿಂದ ಹೊರಟಿದ್ದು <DottedLine /></span>
          <span>ಎಲ್ಲಿಗೆ <DottedLine /></span>
        </div>

        <div>
          ನೋಂದಣಿ ಪುಸ್ತಕ ಅಥವಾ ಪರವಾನಗಿ ಪ್ರಕಾರ ಆಸನಗಳ ಮಿತಿ <DottedLine />
        </div>

        <div>
          ವಾಹನವನ್ನು ತಡೆ ನಿಲ್ಲಿಸಿದಾಗ ಇದ್ದ ಪ್ರಯಾಣಿಕರ ಸಂಖ್ಯೆ <DottedLine />
        </div>

        <div className="mt-2">
          <div>ಅಪರಾಧದ ವಿವರ:</div>
          <div className="space-y-1 mt-1">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="border-b border-dotted border-black h-5 w-full"></div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="text-[10px] mt-3 text-justify">
          ಸಾರಿಗೆ ಲೋಕ ಸಾರಿಗೆ ಅಧಿಕಾರಿಯವರು ಈ ಮೇಲಿನ ಅಪರಾಧದ ಬಗ್ಗೆ ಕಾಯಿದೆಯ ಪ್ರಕಾರ ಏಳು ದಿನದೊಳಗಾಗಿ ಏಕತ್ರ ಕ್ರಮ ಜರುಗಿಸಬಾರದು,
          ಮಾಲೀಕನ/ಚಾಲಕನ/ವಾಹಕನ ಹಾಗೂ ಇತರರ ತತ್ಸರ ವಿರುದ್ಧ ಎಂದು ಮೇಲಾಧಿಕಾರಿಗಳಿಗೆ ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ.
        </div>

        {/* Signatures */}
        <div className="flex justify-between mt-4">
          <div className="text-center">
            <div className="border-b border-black w-32 mx-auto mb-1"></div>
            <div className="text-xs">ಚಾಲಕರ ಸಹಿ</div>
          </div>
          <div className="text-center">
            <div className="border-b border-black w-32 mx-auto mb-1"></div>
            <div className="text-xs">ಅಧಿಕಾರಿಯ ಸಹಿ</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TransportForm;