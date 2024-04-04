import Particles, { initParticlesEngine } from "@tsparticles/react";
import { useEffect, useMemo, useState } from "react";
import { loadSlim } from "@tsparticles/slim";

const ParticlesComponent = (props) => {
    const [init, setInit] = useState(false);

    useEffect(() => {
        initParticlesEngine(async (engine) => {
            await loadSlim(engine);
        }).then(() => {
            setInit(true);
        });
    }, []);

    const particlesLoaded = (container) => {
        console.log(container);
    };

    const options = useMemo(
        () => ({
            autoPlay: true,
            background: {
                color: {
                    value: "#232741"
                },
            },
            backgroundMask: {
                enable: false
            },
            clear: true,
            duration: 0,
            fpsLimit: 120,
            interactivity: {
                detectsOn: "window",
                events: {
                    onClick: {
                        enable: true,
                        mode: "repulse"
                    },
                    onHover: {
                        enable: true,
                        mode: "bubble",
                        radius: 3,
                        parallax: {
                            enable: false
                        }
                    },
                    resize: {
                        enable: true,
                        delay: 0.5
                    }
                },
                modes: {
                    repulse: {
                        distance: 400,
                        duration: 0.4,
                        factor: 100,
                        speed: 1
                    },
                    bubble: {
                        distance: 250,
                        duration: 2,
                        opacity: 0,
                        size: 0
                    }
                }
            },
            detectRetina: true,
            particles: {
                bounce: {
                    horizontal: {
                        value: 1
                    },
                    vertical: {
                        value: 1
                    }
                },
                collisions: {
                    enable: false
                },
                color: {
                    value: "#ffffff"
                },
                links: {
                    enable: false
                },
                move: {
                    enable: true,
                    speed: .5
                },
                number: {
                    density: {
                        enable: true,
                        value_area: 900 // Adjust the density as needed
                    },
                    value: 150
                },
                opacity: {
                    value: 1
                },
                shape: {
                    type: "circle"
                },
                size: {
                    value: { min: 1, max: 3 }
                }
            },
            pauseOnBlur: true,
            pauseOnOutsideViewport: true
        }),
        []
    );

    return <Particles id={props.id} init={particlesLoaded} options={options} />;
};

export default ParticlesComponent;
