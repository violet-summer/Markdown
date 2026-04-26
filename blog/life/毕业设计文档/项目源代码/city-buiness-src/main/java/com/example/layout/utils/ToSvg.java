package com.example.layout.utils;

import com.example.citybusiness.contract.model.*;
import jakarta.validation.Valid;

import java.util.List;

public final class ToSvg {
    public static String toSvgContent(LayoutJson layoutJson) {
        int originX = layoutJson.getOrigin() != null ? layoutJson.getOrigin().getX() : 0;
        int originY = layoutJson.getOrigin() != null ? layoutJson.getOrigin().getY() : 0;
        int worldWidth = layoutJson.getWorldDimensions() != null ? layoutJson.getWorldDimensions().getX() : 1000;
        int worldHeight = layoutJson.getWorldDimensions() != null ? layoutJson.getWorldDimensions().getY() : 1000;
        double baseStrokeWidth = Math.max(worldWidth, worldHeight) / 1000.0;
        String groundStroke = String.valueOf(baseStrokeWidth * 0.5);
        String seaStroke = String.valueOf(baseStrokeWidth * 0.5);
        String coastlineStroke = String.valueOf(baseStrokeWidth * 1.5);
        String riverStroke = String.valueOf(baseStrokeWidth * 0.5);
        String mainRoadStroke = String.valueOf(baseStrokeWidth * 1);
        String majorRoadStroke = String.valueOf(baseStrokeWidth * 1.5);
        String minorRoadStroke = String.valueOf(baseStrokeWidth * 1);
        String parkBigStroke = String.valueOf(baseStrokeWidth * 0.5);
        String parkSmallStroke = String.valueOf(baseStrokeWidth * 0.3);
        String blockStroke = String.valueOf(baseStrokeWidth * 0.3);

        StringBuilder svg = new StringBuilder();
        svg.append("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"")
            .append(worldWidth).append("\" height=\"").append(worldHeight)
            .append("\" viewBox=\"").append(originX).append(" ").append(originY).append(" ")
            .append(worldWidth).append(" ").append(worldHeight)
            .append("\" preserveAspectRatio=\"xMidYMid meet\">\n");

        // Ground layer
        System.out.println("layout svg content"+layoutJson);
        if (layoutJson.getGroundPolygon() != null && layoutJson.getGroundPolygon().size() >= 3) {
            String pts = polyPointsStr(layoutJson.getGroundPolygon());
//            System.out.println(pts);
            if (!pts.isEmpty()) {
                svg.append("  <g id=\"layer-ground\" class=\"layer-ground\">\n");
                svg.append("    <polygon points=\"").append(pts).append("\" fill=\"#d4d4d4\" stroke=\"none\" stroke-width=\"").append(groundStroke).append("\"/>\n");
                svg.append("  </g>\n");
            }
        }
        // Sea layer
        if (layoutJson.getSeaPolygon() != null && layoutJson.getSeaPolygon().size() >= 3) {
            String pts = polyPointsStr(layoutJson.getSeaPolygon());
            if (!pts.isEmpty()) {
                svg.append("  <g id=\"layer-sea\" class=\"layer-sea\">\n");
                svg.append("    <polygon points=\"").append(pts).append("\" fill=\"#87ceeb\" stroke=\"none\" stroke-width=\"").append(seaStroke).append("\"/>\n");
                svg.append("  </g>\n");
            }
        }
        // Coastline layer
        if (layoutJson.getCoastlinePolygon() != null && layoutJson.getCoastlinePolygon().size() >= 2) {
            String pts = polyPointsStr(layoutJson.getCoastlinePolygon());
            if (!pts.isEmpty()) {
                svg.append("  <g id=\"layer-coastline\" class=\"layer-coastline\">\n");
                svg.append("    <polyline points=\"").append(pts).append("\" fill=\"none\" stroke=\"none\" stroke-width=\"").append(coastlineStroke).append("\"/>\n");
                svg.append("  </g>\n");
            }
        }
        // River layer
        if (layoutJson.getRiverPolygon() != null && layoutJson.getRiverPolygon().size() >= 3) {
            String pts = polyPointsStr(layoutJson.getRiverPolygon());
            if (!pts.isEmpty()) {
                svg.append("  <g id=\"layer-river\" class=\"layer-river\">\n");
                svg.append("    <polygon points=\"").append(pts).append("\" fill=\"#2563eb\" stroke=\"none\" stroke-width=\"").append(riverStroke).append("\"/>\n");
                svg.append("  </g>\n");
            }
        }
        // Parks, blocks, divided buildings (List<List<T>>)
        if (layoutJson.getBigParksPolygon() != null) {
            svg.append("  <g id=\"layer-parks-big\" class=\"layer-parks-big\">\n");
            for (List<@Valid LayoutJsonBigParksPolygonInnerInner> park : layoutJson.getBigParksPolygon()) {
                String pts = polyPointsStr(park);
                if (!pts.isEmpty()) {
                    svg.append("    <polygon points=\"").append(pts).append("\" fill=\"#4ade80\" stroke=\"none\" stroke-width=\"").append(parkBigStroke).append("\"/>\n");
                }
            }
            svg.append("  </g>\n");
        }
        if (layoutJson.getBlocksPolygon() != null) {
            svg.append("  <g id=\"layer-blocks\" class=\"layer-blocks\">\n");
            for (List<@Valid LayoutJsonBlocksPolygonInnerInner> block : layoutJson.getBlocksPolygon()) {
                String pts = polyPointsStr(block);
                if (!pts.isEmpty()) {
                    svg.append("    <polygon points=\"").append(pts).append("\" fill=\"#000000\" stroke=\"none\" stroke-width=\"").append(blockStroke).append("\"/>\n");
                }
            }
            svg.append("  </g>\n");
        }
        if (layoutJson.getDividedBuildingsPolygons() != null) {
            svg.append("  <g id=\"layer-divided-buildings\" class=\"layer-divided-buildings\">\n");
            for (List<@Valid LayoutJsonDividedBuildingsPolygonsInnerInner> building : layoutJson.getDividedBuildingsPolygons()) {
                String pts = polyPointsStr(building);
                if (!pts.isEmpty()) {
                    svg.append("    <polygon points=\"").append(pts).append("\" fill=\"#555555\" stroke=\"none\" stroke-width=\"").append(blockStroke).append("\"/>\n");
                }
            }
            svg.append("  </g>\n");
        }
        // Main roads (normal) - polygon闭合且只填充颜色，无描边
        if (layoutJson.getMainNormalRoadPolygon() != null && !layoutJson.getMainNormalRoadPolygon().isEmpty()) {
            svg.append("  <g id=\"layer-roads-main-normal\" class=\"layer-roads-main\">\n");
            for (List<@Valid LayoutJsonMainNormalRoadPolygonInnerInner> road : layoutJson.getMainNormalRoadPolygon()) {
                String pts = polyPointsStr(road);
                if (!pts.isEmpty()) {
                    svg.append("    <polygon points=\"").append(pts).append("\" fill=\"rgb(255,0,0)\" stroke=\"none\" stroke-width=\"").append(mainRoadStroke).append("\"/>\n");
                }
            }
            svg.append("  </g>\n");
        }
        // Main roads (exterior/interior) - path环形填充
        if (layoutJson.getMainExteriorInteriorRoadPolygon() != null && !layoutJson.getMainExteriorInteriorRoadPolygon().isEmpty()) {
            svg.append("  <g id=\"layer-roads-main-exterior-interior\" class=\"layer-roads-main\">\n");
            for (@Valid LayoutJsonMainExteriorInteriorRoadPolygonInner road : layoutJson.getMainExteriorInteriorRoadPolygon()) {
                String d = annulusPathStr(road.getExterior(), road.getInterior());
                if (!d.isEmpty()) {
                    svg.append("    <path d=\"").append(d).append("\" fill=\"#ffcccc\" stroke=\"none\" fill-rule=\"evenodd\" stroke-width=\"").append(mainRoadStroke).append("\"/>\n");
                }
            }
            svg.append("  </g>\n");
        }
        // Major roads (normal) - polygon闭合且只填充颜色，无描边
        if (layoutJson.getMajorNormalRoadPolygon() != null && !layoutJson.getMajorNormalRoadPolygon().isEmpty()) {
            svg.append("  <g id=\"layer-roads-major-normal\" class=\"layer-roads-major\">\n");
            for (List<@Valid LayoutJsonMajorNormalRoadPolygonInnerInner> road : layoutJson.getMajorNormalRoadPolygon()) {
                String pts = polyPointsStr(road);
                if (!pts.isEmpty()) {
                    svg.append("    <polygon points=\"").append(pts).append("\" fill=\"rgb(0,255,0)\" stroke=\"none\" stroke-width=\"").append(majorRoadStroke).append("\"/>\n");
                }
            }
            svg.append("  </g>\n");
        }
        // Major roads (exterior/interior) - path环形填充
        if (layoutJson.getMajorExteriorInteriorRoadPolygon() != null && !layoutJson.getMajorExteriorInteriorRoadPolygon().isEmpty()) {
            svg.append("  <g id=\"layer-roads-major-exterior-interior\" class=\"layer-roads-major\">\n");
            for (@Valid LayoutJsonMajorExteriorInteriorRoadPolygonInner road : layoutJson.getMajorExteriorInteriorRoadPolygon()) {
                String d = annulusPathStr(road.getExterior(), road.getInterior());
                if (!d.isEmpty()) {
                    svg.append("    <path d=\"").append(d).append("\" fill=\"#ccffcc\" stroke=\"none\" fill-rule=\"evenodd\" stroke-width=\"").append(majorRoadStroke).append("\"/>\n");
                }
            }
            svg.append("  </g>\n");
        }
        // Minor roads (normal) - polygon闭合且只填充颜色，无描边
        if (layoutJson.getMinorNormalRoadPolygon() != null && !layoutJson.getMinorNormalRoadPolygon().isEmpty()) {
            svg.append("  <g id=\"layer-roads-minor-normal\" class=\"layer-roads-minor\">\n");
            for (List<@Valid LayoutJsonMinorNormalRoadPolygonInnerInner> road : layoutJson.getMinorNormalRoadPolygon()) {
                String pts = polyPointsStr(road);
                if (!pts.isEmpty()) {
                    svg.append("    <polygon points=\"").append(pts).append("\" fill=\"rgb(0,0,255)\" stroke=\"none\" stroke-width=\"").append(minorRoadStroke).append("\"/>\n");
                }
            }
            svg.append("  </g>\n");
        }
        // Minor roads (exterior/interior) - path环形填充
        if (layoutJson.getMinorExteriorInteriorRoadPolygon() != null && !layoutJson.getMinorExteriorInteriorRoadPolygon().isEmpty()) {
            svg.append("  <g id=\"layer-roads-minor-exterior-interior\" class=\"layer-roads-minor\">\n");
            for (@Valid LayoutJsonMinorExteriorInteriorRoadPolygonInner road : layoutJson.getMinorExteriorInteriorRoadPolygon()) {
                String d = annulusPathStr(road.getExterior(), road.getInterior());
                if (!d.isEmpty()) {
                    svg.append("    <path d=\"").append(d).append("\" fill=\"#ccccff\" stroke=\"none\" fill-rule=\"evenodd\" stroke-width=\"").append(minorRoadStroke).append("\"/>\n");
                }
            }
            svg.append("  </g>\n");
        }
        // Small parks
        if (layoutJson.getSmallParksPolygons() != null && !layoutJson.getSmallParksPolygons().isEmpty()) {
            svg.append("  <g id=\"layer-parks-small\" class=\"layer-parks-small\">\n");
            for (String park : layoutJson.getSmallParksPolygons()) {
                svg.append("    <polygon points=\"").append(park).append("\" fill=\"#86efac\" stroke=\"none\" stroke-width=\"").append(parkSmallStroke).append("\"/>\n");
            }
            svg.append("  </g>\n");
        }
        svg.append("</svg>\n");
        return svg.toString();
    }

    // 一维List<T>的点序列，首尾闭合
    private static <T> String polyPointsStr(List<T> pts) {
        if (pts == null || pts.size() < 3) return "";
        StringBuilder sb = new StringBuilder();
        for (T p : pts) {
            double x = 0, y = 0;
            try {
                Object xObj = p.getClass().getMethod("getX").invoke(p);
                Object yObj = p.getClass().getMethod("getY").invoke(p);
                if (xObj instanceof java.math.BigDecimal) {
                    x = ((java.math.BigDecimal)xObj).doubleValue();
                } else if (xObj instanceof Number) {
                    x = ((Number)xObj).doubleValue();
                }
                if (yObj instanceof java.math.BigDecimal) {
                    y = ((java.math.BigDecimal)yObj).doubleValue();
                } else if (yObj instanceof Number) {
                    y = ((Number)yObj).doubleValue();
                }
            } catch (Exception e) {
                System.out.println("获取点出错"+e.getMessage());
            }
            sb.append(x).append(",").append(y).append(" ");
        }
        // 首尾闭合
        if (pts.size() > 2) {
            try {
                Object x0Obj = pts.get(0).getClass().getMethod("getX").invoke(pts.get(0));
                Object y0Obj = pts.get(0).getClass().getMethod("getY").invoke(pts.get(0));
                Object xnObj = pts.get(pts.size()-1).getClass().getMethod("getX").invoke(pts.get(pts.size()-1));
                Object ynObj = pts.get(pts.size()-1).getClass().getMethod("getY").invoke(pts.get(pts.size()-1));
                double x0 = x0Obj instanceof java.math.BigDecimal ? ((java.math.BigDecimal)x0Obj).doubleValue() : ((Number)x0Obj).doubleValue();
                double y0 = y0Obj instanceof java.math.BigDecimal ? ((java.math.BigDecimal)y0Obj).doubleValue() : ((Number)y0Obj).doubleValue();
                double xn = xnObj instanceof java.math.BigDecimal ? ((java.math.BigDecimal)xnObj).doubleValue() : ((Number)xnObj).doubleValue();
                double yn = ynObj instanceof java.math.BigDecimal ? ((java.math.BigDecimal)ynObj).doubleValue() : ((Number)ynObj).doubleValue();
                if (x0 != xn || y0 != yn) sb.append(x0).append(",").append(y0);
            } catch (Exception ignore) {}
        }
        return sb.toString().trim();
    }
    // 一维List<T>的点序列（不闭合）
    private static <T> String pointsStrNoClose(List<T> pts) {
        if (pts == null || pts.isEmpty()) return "";
        StringBuilder sb = new StringBuilder();
        for (T p : pts) {
            double x = 0, y = 0;
            try {
                x = (double) p.getClass().getMethod("getX").invoke(p);
                y = (double) p.getClass().getMethod("getY").invoke(p);
            } catch (Exception ignore) {}
            sb.append(x).append(",").append(y).append(" ");
        }
        return sb.toString().trim();
    }
    // 生成内外环 path 字符串，强制外环顺时针、内环逆时针，确保SVG环形填充正确
    private static <T, U> String annulusPathStr(List<T> exterior, List<U> interior) {
        if (exterior == null || exterior.size() < 3) return "";
        List<T> extAdj = forceClockwise(exterior);
        StringBuilder sb = new StringBuilder();
        sb.append("M ").append(pointsStrNoClose(extAdj)).append(" Z");
        if (interior != null && interior.size() >= 3) {
            List<U> intAdj = forceCounterClockwise(interior);
            sb.append(" M ").append(pointsStrNoClose(intAdj)).append(" Z");
        }
        return sb.toString();
    }
    // 强制顺时针
    public static <T> List<T> forceClockwise(List<T> pts) {
        if (pts == null || pts.size() < 3) return pts;
        if (!isClockwise(pts)) {
            return reverseList(pts);
        }
        return pts;
    }
    // 强制逆时针
    public static <T> List<T> forceCounterClockwise(List<T> pts) {
        if (pts == null || pts.size() < 3) return pts;
        if (isClockwise(pts)) {
            return reverseList(pts);
        }
        return pts;
    }
    // 判断多边形点序列是否顺时针（Shoelace公式，S<0为顺时针）
    private static <T> boolean isClockwise(List<T> pts) {
        if (pts == null || pts.size() < 3) return false;
        List<T> cleanPts = removeDuplicateEnd(pts);
        double area = 0;
        int n = cleanPts.size();
        for (int i = 0; i < n; i++) {
            double x0 = 0, y0 = 0, x1 = 0, y1 = 0;
            try {
                x0 = (double) cleanPts.get(i).getClass().getMethod("getX").invoke(cleanPts.get(i));
                y0 = (double) cleanPts.get(i).getClass().getMethod("getY").invoke(cleanPts.get(i));
                int j = (i + 1) % n;
                x1 = (double) cleanPts.get(j).getClass().getMethod("getX").invoke(cleanPts.get(j));
                y1 = (double) cleanPts.get(j).getClass().getMethod("getY").invoke(cleanPts.get(j));
            } catch (Exception ignore) {}
            area += (x1 - x0) * (y1 + y0);
        }
        return area < 0; // S<0为顺时针
    }
    // 去除首尾重复点
    private static <T> List<T> removeDuplicateEnd(List<T> pts) {
        if (pts == null || pts.size() < 2) return pts;
        try {
            double x0 = (double) pts.get(0).getClass().getMethod("getX").invoke(pts.get(0));
            double y0 = (double) pts.get(0).getClass().getMethod("getY").invoke(pts.get(0));
            double xn = (double) pts.get(pts.size()-1).getClass().getMethod("getX").invoke(pts.get(pts.size()-1));
            double yn = (double) pts.get(pts.size()-1).getClass().getMethod("getY").invoke(pts.get(pts.size()-1));
            if (x0 == xn && y0 == yn) {
                return pts.subList(0, pts.size()-1);
            }
        } catch (Exception ignore) {}
        return pts;
    }
    // 反转List
    private static <T> List<T> reverseList(List<T> list) {
        java.util.ArrayList<T> rev = new java.util.ArrayList<>(list);
        java.util.Collections.reverse(rev);
        return rev;
    }
}
