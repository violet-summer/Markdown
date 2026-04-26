import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import interact from "interactjs";

export type DraggableCardItem = {
  id: string;
  title: string;
  content: ReactNode;
};

type CardRect = {
  x: number;
  y: number;
  width: number;
  height: number;
};

type DraggableBoardProps = {
  items: DraggableCardItem[];
  storageKey: string;
  scale?: number;
  minCardWidth?: number;
  minCardHeight?: number;
};

const DEFAULT_WIDTH = 240;
const DEFAULT_HEIGHT = 160;

const getStoredRects = (storageKey: string): Record<string, CardRect> => {
  try {
    const raw = window.localStorage.getItem(storageKey);
    if (!raw) {
      return {};
    }
    const parsed = JSON.parse(raw) as Record<string, CardRect>;
    return parsed ?? {};
  } catch {
    return {};
  }
};

const storeRects = (storageKey: string, rects: Record<string, CardRect>) => {
  window.localStorage.setItem(storageKey, JSON.stringify(rects));
};

const defaultRect = (index: number, width: number, height: number): CardRect => {
  const col = index % 2;
  const row = Math.floor(index / 2);
  return {
    x: 12 + col * (width + 16),
    y: 12 + row * (height + 16),
    width,
    height,
  };
};

const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(max, value));

const resolveCollisions = (
  rects: Record<string, CardRect>,
  boardWidth: number,
  boardHeight: number
): Record<string, CardRect> => {
  const ids = Object.keys(rects);
  const next = { ...rects };
  const maxIterations = 20;

  for (let iteration = 0; iteration < maxIterations; iteration += 1) {
    let moved = false;

    for (let i = 0; i < ids.length; i += 1) {
      for (let j = i + 1; j < ids.length; j += 1) {
        const a = next[ids[i]];
        const b = next[ids[j]];
        if (!a || !b) {
          continue;
        }

        const ax2 = a.x + a.width;
        const ay2 = a.y + a.height;
        const bx2 = b.x + b.width;
        const by2 = b.y + b.height;
        const overlapX = Math.min(ax2, bx2) - Math.max(a.x, b.x);
        const overlapY = Math.min(ay2, by2) - Math.max(a.y, b.y);

        if (overlapX > 0 && overlapY > 0) {
          const pushX = overlapX / 2 + 4;
          const pushY = overlapY / 2 + 4;
          if (a.x < b.x) {
            a.x -= pushX;
            b.x += pushX;
          } else {
            a.x += pushX;
            b.x -= pushX;
          }
          if (a.y < b.y) {
            a.y -= pushY;
            b.y += pushY;
          } else {
            a.y += pushY;
            b.y -= pushY;
          }
          moved = true;
        }
      }
    }

    ids.forEach((id) => {
      const rect = next[id];
      rect.x = clamp(rect.x, 0, Math.max(0, boardWidth - rect.width));
      rect.y = clamp(rect.y, 0, Math.max(0, boardHeight - rect.height));
    });

    if (!moved) {
      break;
    }
  }

  return next;
};

export function DraggableBoard({
  items,
  storageKey,
  scale = 1,
  minCardWidth = 200,
  minCardHeight = 140,
}: DraggableBoardProps) {
  const boardRef = useRef<HTMLDivElement | null>(null);
  const [rects, setRects] = useState<Record<string, CardRect>>(() => getStoredRects(storageKey));

  useEffect(() => {
    setRects((current) => {
      let changed = false;
      const next: Record<string, CardRect> = { ...current };
      items.forEach((item, index) => {
        if (!next[item.id]) {
          next[item.id] = defaultRect(index, DEFAULT_WIDTH, DEFAULT_HEIGHT);
          changed = true;
        }
      });
      if (!changed) {
        return current;
      }
      storeRects(storageKey, next);
      return next;
    });
  }, [items, storageKey]);

  useEffect(() => {
    if (!boardRef.current) {
      return;
    }

    const boardElement = boardRef.current;
    const updateRect = (id: string, update: Partial<CardRect>) => {
      setRects((current) => {
        const currentRect = current[id];
        if (!currentRect) {
          return current;
        }
        const nextRect = { ...currentRect, ...update };
        const next = { ...current, [id]: nextRect };
        storeRects(storageKey, next);
        return next;
      });
    };

    const applyCollisionResolution = () => {
      const boardBounds = boardElement.getBoundingClientRect();
      setRects((current) => {
        const resolved = resolveCollisions({ ...current }, boardBounds.width, boardBounds.height);
        storeRects(storageKey, resolved);
        return resolved;
      });
    };

    items.forEach((item) => {
      const selector = `[data-drag-card="${item.id}"]`;
      const cardElement = boardElement.querySelector(selector) as HTMLElement | null;
      if (!cardElement) {
        return;
      }

      interact(cardElement)
        .draggable({
          allowFrom: ".drag-card-handle",
          listeners: {
            move: (event) => {
              setRects((current) => {
                const next = { ...current };
                const rect = next[item.id];
                if (!rect) {
                  return current;
                }
                rect.x += event.dx;
                rect.y += event.dy;
                return next;
              });
            },
            end: () => {
              applyCollisionResolution();
            },
          },
        })
        .resizable({
          edges: { left: true, right: true, bottom: true, top: true },
          listeners: {
            move: (event) => {
              setRects((current) => {
                const next = { ...current };
                const rect = next[item.id];
                if (!rect) {
                  return current;
                }
                rect.width = Math.max(minCardWidth, rect.width + event.deltaRect.width);
                rect.height = Math.max(minCardHeight, rect.height + event.deltaRect.height);
                rect.x += event.deltaRect.left;
                rect.y += event.deltaRect.top;
                return next;
              });
            },
            end: () => {
              applyCollisionResolution();
            },
          },
        });
    });

    return () => {
      items.forEach((item) => {
        const selector = `[data-drag-card="${item.id}"]`;
        const cardElement = boardElement.querySelector(selector) as HTMLElement | null;
        if (cardElement) {
          interact(cardElement).unset();
        }
      });
    };
  }, [items, minCardHeight, minCardWidth, storageKey]);

  return (
    <div
      className="drag-board relative min-h-[260px] overflow-hidden rounded-[12px] border border-dashed border-[var(--border)] bg-[var(--surface-2)]"
      ref={boardRef}
    >
      <div
        className="drag-board-scale relative h-full w-full origin-top-left"
        style={{ transform: `scale(${scale})` }}
      >
        {items.map((item) => {
          const rect = rects[item.id] ?? defaultRect(0, DEFAULT_WIDTH, DEFAULT_HEIGHT);
          return (
            <div
              key={item.id}
              className="drag-card absolute grid min-w-[200px] grid-rows-[auto_1fr] overflow-hidden rounded-[12px] border border-[var(--border)] bg-[var(--surface)] shadow-[0_12px_20px_-16px_var(--shadow)]"
              data-drag-card={item.id}
              style={{
                transform: `translate(${rect.x}px, ${rect.y}px)`,
                width: rect.width,
                height: rect.height,
              }}
            >
              <div className="drag-card-handle flex cursor-grab items-center justify-between bg-[var(--surface-2)] px-2.5 py-1 text-[12px] font-semibold">
                <span>{item.title}</span>
                <span className="drag-card-hint text-[10px] uppercase tracking-[0.12em] text-[var(--muted)]">drag</span>
              </div>
              <div className="drag-card-body grid gap-2 p-2.5">{item.content}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
