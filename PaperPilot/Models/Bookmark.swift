//
//  Bookmark.swift
//  PaperPilot
//
//  Created by 林思行 on 2023/10/15.
//

import Foundation
import SwiftData
import PDFKit

/// 书签
@Model
class Bookmark: Hashable, Identifiable {
    @Attribute(.unique) var id: UUID = UUID()
    /// 页码
    var page: Int
    /// 标签
    var label: String?
    /// 所属论文
    var paperId: Paper.ID
    
    init(paperId: Paper.ID, page: Int, label: String?) {
        self.page = page
        self.paperId = paperId
        self.label = label
    }
}
