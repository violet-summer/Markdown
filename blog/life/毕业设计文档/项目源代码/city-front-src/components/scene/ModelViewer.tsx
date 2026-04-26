import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader.js";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

const DEFAULT_MESSAGE = "Generate a model to preview the scene.";

export interface ModelViewerProps {
  objContents?: string[];
  glbUrls?: string[];
}

export function ModelViewer({ objContents = [], glbUrls = [] }: ModelViewerProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [message, setMessage] = useState(DEFAULT_MESSAGE);
  const [containerSize, setContainerSize] = useState({ width: 800, height: 600 });

  useEffect(() => {
    if (!containerRef.current) return;
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        if (width > 0 && height > 0) {
          setContainerSize({ width: Math.floor(width), height: Math.floor(height) });
        }
      }
    });
    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#f6efe5");

    const camera = new THREE.PerspectiveCamera(50, containerSize.width / containerSize.height, 0.1, 1000);
    camera.position.set(6, 6, 10);

    let renderer: THREE.WebGLRenderer | null = null;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, logarithmicDepthBuffer: true });
      renderer.setPixelRatio(window.devicePixelRatio);
      renderer.setSize(containerSize.width, containerSize.height);
      mount.appendChild(renderer.domElement);
    } catch {
      setMessage("WebGL is not available in this environment.");
      return;
    }

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;

    const ambient = new THREE.AmbientLight(0xffffff, 0.7);
    const directional = new THREE.DirectionalLight(0xffffff, 0.7);
    directional.position.set(6, 8, 4);
    scene.add(ambient, directional);

    const grid = new THREE.GridHelper(12, 12, "#c8b9a5", "#e4d6c5");
    grid.position.y = -0.01;
    scene.add(grid);

    const resize = () => {
      if (!renderer) return;
      renderer.setSize(containerSize.width, containerSize.height);
      camera.aspect = containerSize.width / containerSize.height;
      camera.updateProjectionMatrix();
    };

    const onResize = () => resize();
    resize();
    window.addEventListener("resize", onResize);

    let animationFrame = 0;
    const render = () => {
      if (!renderer) return;
      controls.update();
      renderer.render(scene, camera);
      animationFrame = requestAnimationFrame(render);
    };
    render();

    const clearScene = () => {
      const removable = scene.children.filter(
        (obj) => !(obj instanceof THREE.AmbientLight) && !(obj instanceof THREE.DirectionalLight) && !(obj instanceof THREE.GridHelper)
      );
      removable.forEach((obj) => scene.remove(obj));
    };

    const fitCameraToModels = () => {
      const box = new THREE.Box3();
      let hasBounds = false;

      scene.children.forEach((obj) => {
        if (obj instanceof THREE.AmbientLight || obj instanceof THREE.DirectionalLight || obj instanceof THREE.GridHelper) {
          return;
        }
        const objBox = new THREE.Box3().setFromObject(obj);
        if (objBox.isEmpty()) return;
        box.union(objBox);
        hasBounds = true;
      });

      if (!hasBounds) return;

      const size = box.getSize(new THREE.Vector3());
      const center = box.getCenter(new THREE.Vector3());
      const maxDim = Math.max(size.x, size.y, size.z);

      const fov = THREE.MathUtils.degToRad(camera.fov);
      const fitDistance = (maxDim / 2) / Math.tan(fov / 2);
      const distance = fitDistance * 1.6;

      const direction = new THREE.Vector3(1, 0.75, 1).normalize();
      camera.position.copy(center).add(direction.multiplyScalar(distance));
      camera.near = Math.max(0.05, distance / 20);
      camera.far = Math.max(distance * 8, camera.near + 50);
      camera.updateProjectionMatrix();

      controls.target.copy(center);
      controls.maxDistance = Math.max(distance * 10, 20);
      controls.update();
    };

    const loadGltf = (url: string): Promise<any> => {
      const loader = new GLTFLoader();
      return new Promise((resolve, reject) => {
        loader.load(url, resolve, undefined, reject);
      });
    };

    const applyStableDepth = (root: THREE.Object3D, layer: number) => {
      root.renderOrder = layer;
      root.traverse((child) => {
        child.renderOrder = layer;
        const mesh = child as THREE.Mesh;
        if (!mesh.isMesh) return;
        const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
        materials.forEach((material) => {
          if (!material) return;
          material.polygonOffset = true;
          material.polygonOffsetFactor = -0.5 - layer * 0.25;
          material.polygonOffsetUnits = -1 - layer;
          material.needsUpdate = true;
        });
      });
    };

    const loadModel = async () => {
      clearScene();
      let loadedAny = false;
      let renderLayer = 1;

      if (glbUrls.length > 0) {
        setMessage("Loading GLB models...");
        for (const url of glbUrls) {
          if (!url) continue;
          try {
            // eslint-disable-next-line no-await-in-loop
            const gltf = await loadGltf(url);
            applyStableDepth(gltf.scene, renderLayer);
            scene.add(gltf.scene);
            renderLayer += 1;
            loadedAny = true;
          } catch {
            // 忽略单个模型加载失败，继续加载其他模型
          }
        }
      }

      if (objContents.length > 0) {
        setMessage("Loading OBJ contents...");
        try {
          objContents.forEach((content) => {
            if (!content) return;
            const obj = new OBJLoader().parse(content);
            obj.position.y = 0;
            applyStableDepth(obj, renderLayer);
            scene.add(obj);
            renderLayer += 1;
            loadedAny = true;
          });
        } catch {
          setMessage("Unable to load model. Check obj_content format.");
          return;
        }
      }

      if (loadedAny) {
        fitCameraToModels();
        setMessage("");
      } else {
        setMessage(glbUrls.length > 0 || objContents.length > 0 ? "Unable to load model." : DEFAULT_MESSAGE);
      }
    };
    void loadModel();

    return () => {
      cancelAnimationFrame(animationFrame);
      window.removeEventListener("resize", onResize);
      controls.dispose();
      if (renderer) {
        renderer.dispose();
        if (mount.contains(renderer.domElement)) {
          mount.removeChild(renderer.domElement);
        }
      }
    };
  }, [objContents, glbUrls, containerSize.width, containerSize.height]);

  return (
    <div ref={containerRef} className="relative w-full h-full min-h-0 overflow-hidden rounded-[16px] border border-[var(--border)] bg-[#f6efe5]">
      <div className="w-full h-full" ref={mountRef} />
      {message ? (
        <div className="absolute inset-0 grid place-items-center text-[14px] text-[var(--muted)] backdrop-blur-[2px]">
          {message}
        </div>
      ) : null}
    </div>
  );
}
