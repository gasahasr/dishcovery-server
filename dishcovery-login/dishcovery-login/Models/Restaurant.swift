import Foundation

struct Restaurant: Identifiable {
    let id: String
    let name: String
    let userId: String
    let placeId: String
    let recommendedDishes: String
    let location: String
    let timestamp: Date
    
    init(id: String = UUID().uuidString,
         name: String,
         userId: String,
         placeId: String = "",
         recommendedDishes: String = "",
         location: String = "",
         timestamp: Date = Date()) {
        self.id = id
        self.name = name
        self.userId = userId
        self.placeId = placeId
        self.recommendedDishes = recommendedDishes
        self.location = location
        self.timestamp = timestamp
    }
}

struct DishcoveryResponse: Codable {
    let recommendedDishes: String
    let placeId: String
    
    enum CodingKeys: String, CodingKey {
        case recommendedDishes = "recommended_dishes"
        case placeId = "place_id"
    }
} 