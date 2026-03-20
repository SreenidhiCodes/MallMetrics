# mode 1
from vision.video_analyzer import analyze_video
from analytics.heatmap_generator import generate_shelf_heatmap as generate_heatmap
from analytics.movement_visualizer import customer_behavior
from analytics.behavior_analysis import store_behavior_analysis
from analytics.brand_analysis import brand_popularity_chart
from database.db_manager import init_db, fetch_data   # ✅ important
#mode 2
import  database.zone_db as zone_db
from vision.zone_analyzer import analyze_zones
from analytics.zone_analysis import zone_advanced_report

def main():

    print("🚀 Initializing Database...")
    init_db()

    print("🎬 Running YOLO Retail Analysis...")
    analyze_video()

    print("\n📊 Generating analysis dashboards...")

    rows = fetch_data()   # ✅ ADD THIS LINE

    print("🗺️ Generating Heatmap...")
    generate_heatmap(rows)   # ✅ FIXED

    print("🚶 Customer Movement...")
    customer_behavior()

    print("📋 Behavior Analysis...")
    store_behavior_analysis()

    print("🏆 Brand Popularity...")
    brand_popularity_chart()

    print("\n✅ ALL SYSTEMS COMPLETED SUCCESSFULLY")

# mode 2
    print("\n Initializing Zone Database...")
    zone_db.init_zone_db()
    print("\n🔍 Running Zone Analysis...")
    analyze_zones()

    print("\n📊 Generating Zone Report...")
    zone_advanced_report()


if __name__ == "__main__":
    main()