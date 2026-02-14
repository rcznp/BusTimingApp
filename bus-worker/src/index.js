export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // -----------------------
    // Health
    // -----------------------
    if (url.pathname === "/health") {
      return Response.json({ status: "ok" });
    }

    // -----------------------
    // Get All Stops (optional)
    // -----------------------
    if (url.pathname === "/bus-stops") {
      const limit = parseInt(url.searchParams.get("limit") || "100");

      const { results } = await env.DB.prepare(`
        SELECT bus_stop_code, description, latitude, longitude
        FROM bus_stops
        ORDER BY description
        LIMIT ?
      `)
      .bind(limit)
      .all();

      return Response.json(results);
    }

    // -----------------------
    // Search Stops
    // -----------------------
    if (url.pathname === "/bus-stops/search") {
      const q = url.searchParams.get("q") || "";
      const limit = parseInt(url.searchParams.get("limit") || "10");

      const wildcard = `${q}%`;

      const { results } = await env.DB.prepare(`
        SELECT bus_stop_code, description, latitude, longitude
        FROM bus_stops
        WHERE description LIKE ?
           OR bus_stop_code LIKE ?
        ORDER BY description
        LIMIT ?
      `)
      .bind(wildcard, wildcard, limit)
      .all();

      return Response.json(results);
    }

    // -----------------------
    // Nearby Stops
    // -----------------------
    if (url.pathname === "/bus-stops/nearby") {
      const lat = parseFloat(url.searchParams.get("lat"));
      const lng = parseFloat(url.searchParams.get("lng"));
      const limit = parseInt(url.searchParams.get("limit") || "20");

      if (isNaN(lat) || isNaN(lng)) {
        return new Response("Missing or invalid lat/lng", { status: 400 });
      }

      // Rough bounding box (~2km radius)
      const radiusKm = 2;
      const latDelta = radiusKm / 111;
      const lngDelta = radiusKm / (111 * Math.cos(lat * Math.PI / 180));

      const minLat = lat - latDelta;
      const maxLat = lat + latDelta;
      const minLng = lng - lngDelta;
      const maxLng = lng + lngDelta;

      const { results } = await env.DB.prepare(`
        SELECT bus_stop_code, description, latitude, longitude
        FROM bus_stops
        WHERE latitude BETWEEN ? AND ?
          AND longitude BETWEEN ? AND ?
      `)
      .bind(minLat, maxLat, minLng, maxLng)
      .all();

      // Haversine formula
      function haversine(lat1, lon1, lat2, lon2) {
        const R = 6371000;
        const toRad = x => x * Math.PI / 180;

        const dLat = toRad(lat2 - lat1);
        const dLng = toRad(lon2 - lon1);

        const a =
          Math.sin(dLat / 2) ** 2 +
          Math.cos(toRad(lat1)) *
          Math.cos(toRad(lat2)) *
          Math.sin(dLng / 2) ** 2;

        return 2 * R * Math.asin(Math.sqrt(a));
      }

      const enriched = results.map(stop => ({
        ...stop,
        distance_m: Math.round(
          haversine(lat, lng, stop.latitude, stop.longitude)
        )
      }));

      enriched.sort((a, b) => a.distance_m - b.distance_m);

      return Response.json(enriched.slice(0, limit));
    }

    // -----------------------
    // Get Stop By Code (KEEP LAST)
    // -----------------------
    if (url.pathname.startsWith("/bus-stops/")) {
      const code = url.pathname.split("/").pop();

      const result = await env.DB.prepare(`
        SELECT bus_stop_code, description, latitude, longitude
        FROM bus_stops
        WHERE bus_stop_code = ?
      `)
      .bind(code)
      .first();

      if (!result) {
        return new Response("Not found", { status: 404 });
      }

      return Response.json(result);
    }

    // -----------------------
    // Default
    // -----------------------
    return new Response("Not found", { status: 404 });
  }
};